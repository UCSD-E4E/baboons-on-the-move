"""
CLI Plugin for performing optimization.
"""
from datetime import datetime
from genericpath import exists
import hashlib
from argparse import ArgumentParser, Namespace
import pickle
from sqlite3 import connect
from typing import Dict, List, Tuple
import cv2

import numpy as np
import pandas as pd
import py7zr
from pyrsistent import v
import yaml
from sherlock.utils import approximate_pareto

from firebase_admin import db
from sherlock import Sherlock
from tqdm import tqdm
from library.cli import str2bool

from baboon_tracking.motion_tracker_pipeline import MotionTrackerPipeline
from baboon_tracking.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline
from cli_plugins.cli_plugin import CliPlugin
from library.config import set_config_part, get_config_declaration, get_config_options
from library.dataset import (
    dataset_motion_results_exists,
    get_dataset_path,
    save_dataset_filter_results,
    save_dataset_motion_results,
    get_dataset_motion_results,
)
from library.design_space import get_design_space
from library.firebase import initialize_app, get_dataset_ref
from ..library.region_file import region_factory
from ..library.metrics import Metrics
from library.nas import NAS
from library.region import bb_intersection_over_union

from collections import OrderedDict


class Optimize(CliPlugin):
    """
    CLI Plugin for performing optimization.
    """

    VIDEO_SCORES = {
        "VISO/car/003": (0.92, 0.92, 0.84),
        "VISO/car/004": (0.83, 0.89, 0.85),
        "VISO/car/005": (0.94, 0.88, 0.91),
        "VISO/car/006": (0.88, 0.93, 0.86),
        "VISO/car/007": (0.80, 0.84, 0.80),
        "VISO/car/008": (0.83, 0.85, 0.81),
        "VISO/car/009": (0.93, 0.73, 0.78),
    }

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        self._progress = True

        parser.add_argument(
            "-d",
            "--dataset",
            default="VISO/car/001",
            help="Provides the input dataset for optimization.",
        )

        parser.add_argument(
            "-t",
            "--enable-tracking",
            default="yes",
            type=str2bool,
            help="Enable tracking instead of detection.",
        )

        parser.add_argument(
            "-p",
            "--enable-persist",
            default="no",
            type=str2bool,
            help="Enable persist for particle filter.",
        )

        parser.add_argument(
            "-w",
            "--max-width",
            default=None,
            type=int,
            help="Sets the max width of regions that can be used.",
        )

        parser.add_argument(
            "-l",
            "--max-height",
            default=None,
            type=int,
            help="Sets the max height of regions that can be used.",
        )

        self._runtime_config = {
            "display": False,
            "save": False,
            "timings": False,
            "progress": True,
        }
        self._max_precision = (0, 0, 0)
        self._max_recall = (0, 0, 0)
        self._max_f1 = (0, 0, 0)

        self._tracking_enabled = False

        if self._progress:
            self._progressbar: tqdm = None

    def _print(self, output):
        if self._progress:
            tqdm.write(output)
        else:
            print(output)

    def _get_score(
        self,
        X: np.ndarray,
        y: np.ndarray,
        known_idx: np.ndarray,
        dataset_path: str,
        config_options: List[Tuple[str, np.ndarray]],
        storage_ref: db.Reference,
        current_idx: List[int],
        video_file: str,
        enable_tracking: bool,
        enable_persist: bool,
        max_width: int,
        max_height: int,
        config_hash: str,
    ):
        cache_known_idx_ref = storage_ref.child("known_idx")
        cache_known_idx = cache_known_idx_ref.get() or []
        current_idx_ref = storage_ref.child("current_idx")
        working_idx_ref = storage_ref.child("working_idx")
        last_update_ref = storage_ref.child("last_update")

        max_recall_ref = storage_ref.child("max_recall")
        max_precision_ref = storage_ref.child("max_precision")
        max_f1_ref = storage_ref.child("max_f1")

        path = f"{dataset_path}/img"
        ground_truth_path = f"{dataset_path}/gt/gt.txt"

        working_idx = set(working_idx_ref.get() or [])

        known_idx = set(known_idx).difference(current_idx)
        self._print(str(known_idx))
        for idx in known_idx:
            # Store the value we are working on so that we don't repeat work.
            working_idx.add(int(idx))
            working_idx_ref.set(list(working_idx))

            self._print(
                "=" * 3
                + f"{video_file}:{enable_tracking}:{enable_persist}:{max_width}:{max_height}"
                + "=" * 3
            )

            cache_result_ref = storage_ref.child(str(idx))
            cache_result = cache_result_ref.get()

            if not cache_result:
                for i, (key, _, value_type) in enumerate(config_options):
                    config_value = X[idx, i]
                    if value_type == "int32":
                        config_value = int(config_value)

                    set_config_part(key, config_value)

                if not dataset_motion_results_exists(video_file, idx, config_hash):
                    MotionTrackerPipeline(
                        path, runtime_config=self._runtime_config
                    ).run()
                    save_dataset_motion_results(video_file, idx, config_hash)
                else:
                    self._print("Using previous motion results...")
                    get_dataset_motion_results(video_file, idx, config_hash)

                SqliteParticleFilterPipeline(
                    path, runtime_config=self._runtime_config
                ).run()
                save_dataset_filter_results(
                    video_file, enable_tracking, enable_persist, idx, config_hash
                )

                recall, precision, f1, _ = Metrics(
                    region_factory("./output/results.db"),
                    region_factory(ground_truth_path),
                    max_width=max_width,
                    max_height=max_height,
                ).calculate_metrics()

                cache_result_ref.set((recall, precision, f1))
                cache_known_idx.append(int(idx))
                cache_known_idx_ref.set(cache_known_idx)

            else:
                self._print("Using Cache...")
                recall, precision, f1 = cache_result

            if idx in known_idx:
                current_idx.append(int(idx))

            y[idx, :] = np.array([recall, precision, f1])
            if np.sum(y[idx, :]) == 0:
                y[idx, :] = np.array([1e-5, 1e-5, 1e-5])

            y[idx, :] /= 1

            max_recall, _, _ = self._max_recall
            _, max_precision, _ = self._max_precision
            _, _, max_f1 = self._max_f1

            if video_file in Optimize.VIDEO_SCORES:
                (
                    required_recall,
                    required_precision,
                    required_f1,
                ) = Optimize.VIDEO_SCORES[video_file]
            else:
                required_recall, required_precision, required_f1 = (2, 2, 2)

            recall_color = "\033[0m"
            if max_recall < recall:
                self._max_recall = (recall, precision, f1)
                max_recall = recall
                recall_color = "\033[93m"

            max_recall_color = recall_color
            if max_recall >= required_recall:
                max_recall_color = "\033[94m"
            else:
                max_recall_color = "\033[91m"

            precision_color = "\033[0m"
            if max_precision < precision:
                self._max_precision = (recall, precision, f1)
                max_precision = precision
                precision_color = "\033[93m"

            max_precision_color = precision_color
            if max_precision >= required_precision:
                max_precision_color = "\033[94m"
            else:
                max_precision_color = "\033[91m"

            f1_color = "\033[0m"
            if max_f1 < f1:
                self._max_f1 = (recall, precision, f1)
                max_f1 = f1
                f1_color = "\033[93m"

            max_f1_color = f1_color
            if max_f1 >= required_f1:
                max_f1_color = "\033[94m"
            else:
                max_f1_color = "\033[91m"

            self._print(
                f"\033[1mCompleted {idx:} at {datetime.utcnow().isoformat()} with Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_recall
            self._print(
                f"{recall_color}Max Recall: {max_recall_color}Recall: {recall:.2f}/{required_recall}{recall_color} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_precision
            self._print(
                f"{precision_color}Max Precision: Recall: {recall:.2f} {max_precision_color}Precision: {precision:.2f}/{required_precision}{precision_color} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_f1
            self._print(
                f"{f1_color}Max F1: Recall: {recall:.2f} Precision: {precision:.2f} {max_f1_color}F1: {f1:.2f}/{required_f1}\033[0m"
            )

            current_idx = list(OrderedDict.fromkeys(current_idx))

            max_recall_ref.set(self._max_recall)
            max_precision_ref.set(self._max_precision)
            max_f1_ref.set(self._max_f1)
            current_idx_ref.set(current_idx)
            last_update_ref.set(datetime.utcnow().isoformat())

            working_idx = set(working_idx_ref.get() or [])
            if int(idx) in working_idx:
                working_idx.remove(int(idx))
            working_idx_ref.set(list(working_idx))

            current_outputs = np.array(y[current_idx, :])
            current_outputs_order = np.argsort(current_outputs[:, 0])
            current_outputs = current_outputs[current_outputs_order, :]
            ypredict, ypredict_idx, _ = approximate_pareto(current_outputs)
            area = np.trapz(ypredict[:, 1], x=ypredict[:, 0])
            self._print(f"Area: {area}")

            current_idx_np = np.array(current_idx)
            if idx in current_idx_np[ypredict_idx]:
                self._print("\033[93mNew Pareto Optimal point found.\033[0m")
            else:
                self._print("No new Pareto Optimal point found.")

            if self._progress and idx in known_idx:
                self._progressbar.n = len(current_idx)
                self._progressbar.refresh()

    def _unpack(self, array: np.ndarray):
        recall, precision, f1 = array

        return float(recall), float(precision), float(f1)

    def execute(self, args: Namespace):
        np.random.seed(1234)  # Allow our caching to be more effective

        initialize_app()

        self._runtime_config["enable_tracking"] = args.enable_tracking
        self._runtime_config["enable_persist"] = args.enable_persist
        self._tracking_enabled = args.enable_tracking

        with open("./config_declaration.yml", "rb") as f:
            config_hash = hashlib.md5(f.read()).hexdigest()

        video_file = args.dataset

        dataset_path = get_dataset_path(video_file)

        max_width: int = args.max_width
        max_height: int = args.max_height

        self._print(max_width)

        if max_width is None or max_height is None:
            img = cv2.imread(f"{dataset_path}/img/000001.jpg")
            frame_height, frame_width, _ = img.shape

            max_width = max_width or frame_width
            max_height = max_height or frame_height

        sherlock_ref = db.reference("sherlock")
        video_file_ref = get_dataset_ref(video_file, sherlock_ref)
        config_declaration_ref = video_file_ref.child(config_hash)

        if args.enable_tracking:
            tracking_ref = config_declaration_ref.child("tracking_enabled")
        else:
            tracking_ref = config_declaration_ref.child("tracking_disabled")

        if args.enable_persist:
            persist_ref = tracking_ref.child("persist_enabled")
        else:
            persist_ref = tracking_ref.child("persist_disabled")

        max_width_ref = persist_ref.child(f"max_width_{max_width}")
        max_height_ref = max_width_ref.child(f"max_height_{max_height}")

        design_space_size_ref = config_declaration_ref.child("design_space_size")

        X, y, current_idx, _ = get_design_space(
            video_file, args.enable_tracking, args.enable_persist
        )

        with open("./config_declaration.yml", "r", encoding="utf8") as f:
            config_declaration = get_config_declaration("", yaml.safe_load(f))
            f.seek(0)

        config_options = [
            (k, get_config_options(i), i["type"])
            for k, i in config_declaration.items()
            if "skip_learn" not in i or not i["skip_learn"]
        ]

        design_space_size_ref.set(X.shape[0])

        percent = 0.3
        budget = int(X.shape[0] * percent)

        if self._progress:
            self._progressbar = tqdm(total=budget, position=1)

        sherlock = Sherlock(
            n_init=5,
            budget=budget,
            surrogate_type="rbfthin_plate-rbf_multiquadric-randomforest-gpy",
            kernel="matern",
            num_restarts=0,
            pareto_margin=0,
            y_hint=None,
            plot_design_space=False,
            use_ted_in_loop=True,
            request_output=lambda y, idx: self._get_score(
                X,
                y,
                idx,
                dataset_path,
                config_options,
                max_height_ref,
                current_idx,
                video_file,
                args.enable_tracking,
                args.enable_persist,
                max_width,
                max_height,
                config_hash,
            ),
            action_only=None,
            n_hint_init=0,
            scale_output=True,
            use_trace_as_prior=True,
            model_selection_type="mab10",
        )

        if self._progress:
            self._progressbar.update(len(current_idx))

        max_recall_idx = np.argmax(y[:, 0])
        max_precision_idx = np.argmax(y[:, 1])
        max_f1_idx = np.argmax(y[:, 2])

        self._max_precision = self._unpack(y[max_recall_idx, :])
        self._max_recall = self._unpack(y[max_precision_idx, :])
        self._max_f1 = self._unpack(y[max_f1_idx, :])

        input_known_idx = np.array(current_idx).astype(int)
        y_known_idx = y[input_known_idx, :]
        y_known_idx[np.sum(y_known_idx, axis=1) == 0, :] += np.array([1e-5, 1e-5, 1e-5])
        y_known_idx /= 1
        y[input_known_idx, :] = y_known_idx

        sherlock.fit(X).predict(X, y, input_known_idx=np.array(current_idx).astype(int))

        if self._progress:
            self._progressbar.close()
