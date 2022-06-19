"""
CLI Plugin for performing optimization.
"""
from datetime import datetime
import hashlib
from argparse import ArgumentParser, Namespace
from sqlite3 import connect
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
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
from library.firebase import initialize_app
from library.region import bb_intersection_over_union


class Optimize(CliPlugin):
    """
    CLI Plugin for performing optimization.
    """

    # VIDEO_FILES = [
    #     "VISO/car/003",  # Video 1
    #     # "VISO/car/004",  # Video 2
    #     # "VISO/car/005",  # Video 3
    #     # "VISO/car/006",  # Video 4
    #     # "VISO/car/007",  # Video 5
    #     # "VISO/car/008",  # Video 6
    #     # "VISO/car/009",  # Video 7
    # ]

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
            "-c",
            "--count",
            default=-1,
            help="The number of frames to use for the video processing. -1 reprsents all frames.",
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
                if identity not in identity_map:
                    matches = np.array(
                        [bb_intersection_over_union(current, t[1:]) for t in truth]
                    )
                    match_idx = np.argmax(matches)
                    score = matches[match_idx]
                    truth_identity = truth[match_idx, 0]

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

    def _get_score(
        self,
        X: np.ndarray,
        y: np.ndarray,
        known_idx: np.ndarray,
        dataset_path: str,
        config_options: List[Tuple[str, np.ndarray]],
        count: int,
        storage_ref: db.Reference,
        current_idx: List[int],
    ):
        cache_known_idx_ref = storage_ref.child("known_idx")
        cache_known_idx = cache_known_idx_ref.get() or []
        current_idx_ref = storage_ref.child("current_idx")
        last_update_ref = storage_ref.child("last_update")

        requested_idx_ref = storage_ref.child("requested_idx")
        requested_idx = requested_idx_ref.get() or []
        requested_idx.extend(known_idx)
        requested_idx = np.array(requested_idx)
        self._print(str(requested_idx))

        max_recall_ref = storage_ref.child("max_recall")
        max_precision_ref = storage_ref.child("max_precision")
        max_f1_ref = storage_ref.child("max_f1")

        path = f"{dataset_path}/img"
        ground_truth_path = f"{dataset_path}/gt/gt.txt"

        for idx in requested_idx:
            cache_result_ref = storage_ref.child(str(idx))
            cache_result = cache_result_ref.get()

            if not cache_result:
                for i, (key, _, value_type) in enumerate(config_options):
                    config_value = X[idx, i]
                    if value_type == "int32":
                        config_value = int(config_value)

                    set_config_part(key, config_value)

                try:
                    if count == -1:
                        count = None

                    MotionTrackerPipeline(
                        path, runtime_config=self._runtime_config
                    ).run(count)
                    SqliteParticleFilterPipeline(
                        path, runtime_config=self._runtime_config
                    ).run(count)

                    recall, precision, f1 = self._get_metrics(
                        "./output/results.db", ground_truth_path
                    )
                except ValueError:
                    recall, precision, f1 = 0, 0, 0

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

            recall_color = "\033[0m"
            if max_recall < recall:
                self._max_recall = (recall, precision, f1)
                recall_color = "\033[93m"

            precision_color = "\033[0m"
            if max_precision < precision:
                self._max_precision = (recall, precision, f1)
                precision_color = "\033[93m"

            f1_color = "\033[0m"
            if max_f1 < f1:
                self._max_f1 = (recall, precision, f1)
                f1_color = "\033[93m"

            self._print(
                f"\033[1mCompleted {idx:} at {datetime.utcnow().isoformat()} with Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_recall
            self._print(
                f"{recall_color}Max Recall: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_precision
            self._print(
                f"{precision_color}Max Precision: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_f1
            self._print(
                f"{f1_color}Max F1: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            self._print("=" * 10)

            max_recall_ref.set(self._max_recall)
            max_precision_ref.set(self._max_precision)
            max_f1_ref.set(self._max_f1)
            current_idx_ref.set(current_idx)
            last_update_ref.set(datetime.utcnow().isoformat())

            requested_idx = {int(r) for r in requested_idx}
            requested_idx_new = requested_idx_ref.get() or []
            requested_idx_new = [r for r in requested_idx_new if r not in requested_idx]
            requested_idx_ref.set(list(set(requested_idx_new)))

            if self._progress:
                self._progressbar.update(1)

    def execute(self, args: Namespace):
        np.random.seed(1234)  # Allow our caching to be more effective

        initialize_app()

        self._runtime_config["enable_tracking"] = args.enable_tracking
        self._runtime_config["enable_persist"] = args.enable_persist
        self._tracking_enabled = args.enable_tracking

        with open("./config_declaration.yml", "rb") as f:
            config_hash = hashlib.md5(f.read()).hexdigest()

        dataset_path = get_dataset_path(args.dataset)
        video_file = dataset_path.split("/")[-1]

        sherlock_ref = db.reference("sherlock")
        video_file_ref = sherlock_ref.child(video_file)
        config_declaration_ref = video_file_ref.child(config_hash)

        if args.enable_tracking:
            tracking_ref = config_declaration_ref.child("tracking_enabled")
        else:
            tracking_ref = config_declaration_ref.child("tracking_disabled")

        if args.enable_persist:
            persist_ref = tracking_ref.child("persist_enabled")
        else:
            persist_ref = tracking_ref.child("persist_disabled")

        frame_count_ref = persist_ref.child(args.count)
        current_idx = []
        design_space_size_ref = config_declaration_ref.child("design_space_size")

        with open("./config_declaration.yml", "r", encoding="utf8") as f:
            config_declaration = get_config_declaration("", yaml.safe_load(f))
            f.seek(0)

        config_options = [
            (k, get_config_options(i), i["type"])
            for k, i in config_declaration.items()
            if "skip_learn" not in i or not i["skip_learn"]
        ]
        X = np.array(np.meshgrid(*[c for _, c, _ in config_options])).T.reshape(
            -1, len(config_options)
        )
        y = np.zeros((X.shape[0], 3))

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
                int(args.count),
                frame_count_ref,
                current_idx,
            ),
            action_only=None,
            n_hint_init=0,
            scale_output=True,
            use_trace_as_prior=True,
            model_selection_type="mab10",
        )

        sherlock.fit(X).predict(X, y)

        if self._progress:
            self._progressbar.close()
