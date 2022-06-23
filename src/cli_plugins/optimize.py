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

import numpy as np
import pandas as pd
import py7zr
import yaml

from firebase_admin import db
from sherlock import Sherlock
from tqdm import tqdm
from cli_plugins.run import str2bool

from baboon_tracking.motion_tracker_pipeline import MotionTrackerPipeline
from baboon_tracking.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline
from cli_plugins.cli_plugin import CliPlugin
from library.config import set_config_part, get_config_declaration, get_config_options
from library.dataset import get_dataset_path
from library.design_space import get_design_space
from library.firebase import initialize_app, get_dataset_ref
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

    def _get_metrics(self, results_db_path: str, ground_truth_path: str):
        with connect(results_db_path) as connection:
            cursor = connection.cursor()

            ground_truth = pd.read_csv(ground_truth_path).to_numpy()

            found_regions = cursor.execute(
                "SELECT x1, y1, x2, y2, identity, frame FROM regions ORDER BY frame"
            )

            curr_frame = -1
            true_positive = 0
            false_negative = 0
            false_positive = 0
            truth = None
            identity_map = {}
            for x1, y1, x2, y2, identity, frame in found_regions:
                if curr_frame != frame:
                    if truth is not None:
                        false_negative += truth.shape[0]

                    truth = np.array(
                        [
                            (truth_identity, x1, y1, x1 + width, y1 + height)
                            for truth_identity, x1, y1, width, height in ground_truth[
                                ground_truth[:, 0] == frame, 1:6
                            ]
                        ]
                    )
                    curr_frame = frame

                current = (x1, y1, x2, y2)
                if identity not in identity_map or not np.any(
                    truth[:, 0] == identity_map[identity]
                ):
                    matches = np.array(
                        [bb_intersection_over_union(current, t[1:]) for t in truth]
                    )
                    if matches.size:
                        match_idx = np.argmax(matches)
                        score = matches[match_idx]
                        truth_identity = truth[match_idx, 0]
                    else:
                        score = 0

                    if score > 0 and self._tracking_enabled:
                        identity_map[identity] = truth_identity
                else:
                    truth_identity = identity_map[identity]
                    match_idx = np.argmax(truth[:, 0] == truth_identity)
                    score = bb_intersection_over_union(current, truth[match_idx, 1:])

                if score > 0:
                    true_positive += 1
                    truth = np.delete(truth, match_idx, 0)
                else:
                    false_positive += 1

        if true_positive == 0:
            false_negative = ground_truth.shape[0]

        recall = true_positive / (false_negative + true_positive)
        if false_positive == 0 and true_positive == 0:
            precision = 0
        else:
            precision = true_positive / (true_positive + false_positive)

        if recall == 0 or precision == 0:
            f1 = 0
        else:
            f1 = (2 * recall * precision) / (recall + precision)

        return recall, precision, f1

    def _save_results(self, video_file: str, idx: int, config_hash: str):
        with py7zr.SevenZipFile("./output/results.db.7z", "w") as archive:
            archive.write("./output/results.db")

        nas = NAS()
        nas.upload_file(
            f"/baboons/Results/{video_file}/{config_hash}/{idx}",
            "./output/results.db.7z",
        )

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
        config_hash: str,
    ):
        cache_known_idx_ref = storage_ref.child("known_idx")
        cache_known_idx = cache_known_idx_ref.get() or []
        current_idx_ref = storage_ref.child("current_idx")
        last_update_ref = storage_ref.child("last_update")

        requested_idx_ref = storage_ref.child("requested_idx")
        requested_idx = []
        requested_idx.extend(known_idx)
        requested_idx = np.array(requested_idx)
        self._print(str(requested_idx))

        max_recall_ref = storage_ref.child("max_recall")
        max_precision_ref = storage_ref.child("max_precision")
        max_f1_ref = storage_ref.child("max_f1")

        path = f"{dataset_path}/img"
        ground_truth_path = f"{dataset_path}/gt/gt.txt"

        for idx in requested_idx:
            self._print("=" * 3 + video_file + "=" * 3)

            cache_result_ref = storage_ref.child(str(idx))
            cache_result = cache_result_ref.get()

            if not cache_result:
                for i, (key, _, value_type) in enumerate(config_options):
                    config_value = X[idx, i]
                    if value_type == "int32":
                        config_value = int(config_value)

                    set_config_part(key, config_value)

                MotionTrackerPipeline(path, runtime_config=self._runtime_config).run()
                SqliteParticleFilterPipeline(
                    path, runtime_config=self._runtime_config
                ).run()

                recall, precision, f1 = self._get_metrics(
                    "./output/results.db", ground_truth_path
                )
                self._save_results(video_file, idx, config_hash)

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
                recall_color = "\033[93m"
            elif max_recall >= required_recall:
                recall_color = "\033[94m"

            precision_color = "\033[0m"
            if max_precision < precision:
                self._max_precision = (recall, precision, f1)
                precision_color = "\033[93m"
            elif max_precision >= required_precision:
                precision_color = "\033[94m"

            f1_color = "\033[0m"
            if max_f1 < f1:
                self._max_f1 = (recall, precision, f1)
                f1_color = "\033[93m"
            elif max_f1 >= required_f1:
                f1_color = "\033[94m"

            self._print(
                f"\033[1mCompleted {idx:} at {datetime.utcnow().isoformat()} with Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_recall
            self._print(
                f"{recall_color}Max Recall: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m => {required_recall}"
            )
            recall, precision, f1 = self._max_precision
            self._print(
                f"{precision_color}Max Precision: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m => {required_precision}"
            )
            recall, precision, f1 = self._max_f1
            self._print(
                f"{f1_color}Max F1: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m => {required_f1}"
            )

            current_idx = list(OrderedDict.fromkeys(current_idx))

            max_recall_ref.set(self._max_recall)
            max_precision_ref.set(self._max_precision)
            max_f1_ref.set(self._max_f1)
            current_idx_ref.set(current_idx)
            last_update_ref.set(datetime.utcnow().isoformat())

            requested_idx = {int(r) for r in requested_idx}
            requested_idx_new = requested_idx_ref.get() or []
            requested_idx_new = [r for r in requested_idx_new if r not in requested_idx]
            requested_idx_ref.set(list(set(requested_idx_new)))

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
            use_ted_in_loop=False,
            request_output=lambda y, idx: self._get_score(
                X,
                y,
                idx,
                dataset_path,
                config_options,
                persist_ref,
                current_idx,
                video_file,
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

        sherlock.fit(X).predict(X, y, input_known_idx=np.array(current_idx).astype(int))

        if self._progress:
            self._progressbar.close()
