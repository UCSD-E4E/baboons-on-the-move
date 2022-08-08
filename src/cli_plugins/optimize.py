"""
CLI Plugin for performing optimization.
"""
import pickle

from argparse import ArgumentParser, Namespace
from os.path import exists
from sqlite3 import connect
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import yaml

from sherlock import Sherlock
from sherlock.utils import adrs

from baboon_tracking import BaboonTracker
from baboon_tracking.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline
from cli_plugins.cli_plugin import CliPlugin
from library.config import get_config, set_config_part
from library.dataset import get_dataset_path
from library.region import bb_intersection_over_union


class Optimize(CliPlugin):
    """
    CLI Plugin for performing optimization.
    """

    VIDEO_FILES = [
        "VISO/car/003",  # Video 1
        # "VISO/car/009", # Video 7
    ]

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        self._score_count = 0
        self._runtime_config = {"display": False, "save": True, "timings": False}
        self._max_precision = (0, 0, 0)
        self._max_recall = (0, 0, 0)
        self._max_f1 = (0, 0, 0)

    def _extend(self, target: Dict[str, Any], source: Dict[str, Any]):
        for key, value in source.items():
            target[key] = value

        return target

    def _get_config_declaration(self, root: str, config_declaration: Dict[str, Any]):
        leaf_nodes = {}

        for key, value in config_declaration.items():
            if isinstance(value, dict):
                self._extend(
                    leaf_nodes, self._get_config_declaration(f"{root}/{key}", value)
                )
                continue

        if not leaf_nodes.keys():
            leaf_nodes[root] = config_declaration

        return leaf_nodes

    def _get_config_options(self, config_declaration: Dict[str, Any]):
        type_value = None
        if config_declaration["type"] == "int32":
            type_value = np.int32
        elif config_declaration["type"] == "float":
            type_value = np.float32

        if "step" in config_declaration:
            step = config_declaration["step"]
        else:
            step = 1

        if "min" in config_declaration:
            min_value = config_declaration["min"]
        else:
            min_value = 0

        if "max" in config_declaration:
            max_value = config_declaration["max"]
        else:
            max_value = 100

        if "odd" in config_declaration:
            is_odd = config_declaration["odd"]
        else:
            is_odd = False

        if is_odd:
            min_value -= 1
            max_value = max_value / 2

        values = np.arange(min_value, max_value, step=step, dtype=type_value)
        if is_odd:
            values = values * 2 + 1

        return values

    def _get_metrics(self, results_db_path: str, ground_truth_path: str):
        with connect(results_db_path) as connection:
            cursor = connection.cursor()

            ground_truth = pd.read_csv(ground_truth_path).to_numpy()
            found_regions = cursor.execute(
                "SELECT x1, y1, x2, y2, identity, frame FROM computed_regions WHERE observed = 1 ORDER BY frame"
            )

            counts = {}
            for x1, y1, x2, y2, identity, frame in found_regions:
                if identity not in counts:
                    counts[identity] = 0

                counts[identity] += 1

            found_regions = cursor.execute(
                "SELECT x1, y1, x2, y2, identity, frame FROM computed_regions WHERE observed = 1 ORDER BY frame"
            )

            curr_frame = -1
            true_positive = 0
            false_negative = 0
            false_positive = 0
            truth = None
            for x1, y1, x2, y2, identity, frame in found_regions:
                if curr_frame != frame:
                    if truth is not None:
                        false_negative += truth.shape[0]

                    truth = np.array(
                        [
                            (x1, y1, x1 + width, y1 + height)
                            for x1, y1, width, height in ground_truth[
                                ground_truth[:, 0] == frame, 2:6
                            ]
                        ]
                    )
                    curr_frame = frame

                # Skip regions that only show up for one frame
                if counts[identity] == 1:
                    continue

                current = (x1, y1, x2, y2)
                matches = np.array(
                    [bb_intersection_over_union(current, t) for t in truth]
                )

                if np.sum(matches) > 0:
                    true_positive += 1
                    truth = truth[np.logical_not(matches == np.max(matches))]
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
        video_file: str,
        config_options: List[Tuple[str, np.ndarray]],
    ):
        if exists("./score_cache.pickle"):
            with open("./score_cache.pickle", "rb") as f:
                score_cache = pickle.load(f)
        else:
            score_cache = {}

        if video_file not in score_cache:
            score_cache[video_file] = {}
        video_score_cache = score_cache[video_file]

        path = get_dataset_path(video_file)
        ground_truth_path = f"./data/Datasets/{video_file}/gt/gt.txt"
        for idx in known_idx:
            hash_str = str(X[idx, :])

            if hash_str not in video_score_cache:
                for i, (key, _, value_type) in enumerate(config_options):
                    config_value = X[idx, i]
                    if value_type == "int32":
                        config_value = int(config_value)

                    set_config_part(key, config_value)

                try:
                    baboon_tracker = BaboonTracker(
                        path, runtime_config=self._runtime_config
                    )
                    baboon_tracker.run(20)
                    particle_filter = SqliteParticleFilterPipeline(
                        path, runtime_config=self._runtime_config
                    )
                    particle_filter.run(20)

                    recall, precision, f1 = self._get_metrics(
                        "./output/results.db", ground_truth_path
                    )
                    video_score_cache[hash_str] = (recall, precision, f1)
                except ValueError:
                    recall, precision, f1 = 0, 0, 0
                    video_score_cache[hash_str] = (recall, precision, f1)

                with open("./score_cache.pickle", "wb") as f:
                    pickle.dump(score_cache, f)

            recall, precision, f1 = video_score_cache[hash_str]

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

            self._score_count += 1
            print(
                f"\033[1mCompleted ({self._score_count / X.shape[0] * 100:.2f}%): {idx:} with Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_recall
            print(
                f"{recall_color}Max Recall: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_precision
            print(
                f"{precision_color}Max Precision: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            recall, precision, f1 = self._max_f1
            print(
                f"{f1_color}Max F1: Recall: {recall:.2f} Precision: {precision:.2f} F1: {f1:.2f}\033[0m"
            )
            print("=" * 10)

    def execute(self, args: Namespace):
        for video_file in Optimize.VIDEO_FILES:
            with open("./config_declaration.yml", "r", encoding="utf8") as f:
                config_declaration = self._get_config_declaration("", yaml.safe_load(f))

            config_options = [
                (k, self._get_config_options(i), i["type"])
                for k, i in config_declaration.items()
                if "skip_learn" not in i or not i["skip_learn"]
            ]
            X = np.array(np.meshgrid(*[c for _, c, _ in config_options])).T.reshape(
                -1, len(config_options)
            )
            y = np.zeros((X.shape[0], 3))

            sherlock = Sherlock(
                n_init=5,
                budget=int(X.shape[0] * 0.2),
                surrogate_type="rbfthin_plate-rbf_multiquadric-randomforest-gpy",
                kernel="matern",
                num_restarts=0,
                pareto_margin=0,
                y_hint=None,
                plot_design_space=False,
                use_ted_in_loop=False,
                request_output=lambda y, idx: self._get_score(
                    X, y, idx, video_file, config_options
                ),
                action_only=None,
                n_hint_init=0,
                scale_output=True,
                use_trace_as_prior=True,
                model_selection_type="mab10",
            )

            sherlock.fit(X).predict(X, y)

            print(sherlock.known_idx)
