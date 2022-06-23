"""
Plugin for calculating metrics.
"""
from argparse import ArgumentParser, Namespace
import hashlib
from typing import Dict, List
import numpy as np
import pandas as pd
from sqlite3 import connect
import py7zr

import yaml
from cli_plugins.cli_plugin import CliPlugin
from library.config import get_config_declaration, get_config_options, set_config_part
from library.firebase import initialize_app
from firebase_admin import db
from library.dataset import get_dataset_path
from baboon_tracking import MotionTrackerPipeline
from baboon_tracking.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline
from library.nas import NAS
from library.region import bb_intersection_over_union
from library.design_space import get_design_space

flatten = lambda t: [item for sublist in t for item in sublist]


class CalculateMetrics(CliPlugin):
    """
    Handles calculating metrics.
    """

    VIDEO_FILES = [
        "VISO/car/003",
        "VISO/car/004",
        "VISO/car/005",
        "VISO/car/006",
        "VISO/car/007",
        "VISO/car/008",
        "VISO/car/009",
    ]

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        self._connection = None
        self._cursor = None

        self._enable_tracking = True
        self._enable_persist = False

        self._runtime_config = {
            "display": False,
            "save": True,
            "timings": False,
            "progress": True,
            "enable_tracking": self._enable_tracking,
            "enable_persist": self._enable_persist,
        }

    def _get_storage_ref(self, video_name: str, config_hash: str):
        results_ref = db.reference("results")
        video_name_ref = results_ref.child(video_name)
        config_declaration_ref = video_name_ref.child(config_hash)

        if self._enable_tracking:
            tracking_ref = config_declaration_ref.child("tracking_enabled")
        else:
            tracking_ref = config_declaration_ref.child("tracking_disabled")

        if self._enable_persist:
            persist_ref = tracking_ref.child("persist_enabled")
        else:
            persist_ref = tracking_ref.child("persist_disabled")

        return persist_ref

    def _get_requests(self, config_hash: str) -> Dict[str, List[int]]:
        results = {}

        for video_file in CalculateMetrics.VIDEO_FILES:
            dataset_path = get_dataset_path(video_file)
            video_name = dataset_path.split("/")[-1]

            storage_ref = self._get_storage_ref(video_name, config_hash)
            requested_idx_ref = storage_ref.child("requested_idx")
            known_idx_ref = storage_ref.child("known_idx")

            requested_idx = set(requested_idx_ref.get() or [])
            known_idx = set(known_idx_ref.get() or [])

            # In case we new known_idx have shown up
            requested_idx.difference_update(known_idx)

            results[video_name] = list(requested_idx)

        return results

    def _get_request(self, requests: Dict[str, List[int]]):
        for video_name, requested_idx in requests.items():
            for idx in requested_idx:
                # idx loop doesn't run if requested_idx is empty
                return video_name, idx

    def _remove_requested_idx(self, video_name: str, idx: int, config_hash: str):
        storage_ref = self._get_storage_ref(video_name, config_hash)
        requested_idx_ref = storage_ref.child("requested_idx")

        requested_idx = set(requested_idx_ref.get() or [])
        if idx in requested_idx:
            requested_idx.remove(idx)
            requested_idx_ref.set(list(requested_idx))

    def _set_config(self, idx: int, X: np.ndarray, config_options):
        for i, (key, _, value_type) in enumerate(config_options):
            config_value = X[idx, i]
            if value_type == "int32":
                config_value = int(config_value)

            set_config_part(key, config_value)

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

                    if score > 0 and self._enable_tracking:
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

    def _set_known_idx(
        self,
        video_name: str,
        idx: int,
        config_hash: str,
        recall: float,
        precision: float,
        f1: float,
    ):
        storage_ref = self._get_storage_ref(video_name, config_hash)

        known_idx_ref = storage_ref.child("known_idx")
        known_idx = set(known_idx_ref.get() or [])
        known_idx.add(idx)
        known_idx_ref.set(list(known_idx))

        idx_ref = storage_ref.child(str(idx))
        idx_ref.set((recall, precision, f1))

    def _save_results(self, video_name: str, idx: int, config_hash: str):
        with py7zr.SevenZipFile("./output/results.db.7z", "w") as archive:
            archive.write("./output/results.db")

        nas = NAS()
        nas.upload_file(
            f"/baboons/Results/VISO/car/{video_name}/{config_hash}/{idx}",
            "./output/results.db.7z",
        )

    def execute(self, args: Namespace):
        """
        Calculate metrics for the specified video and output to Firebase.
        """

        initialize_app()

        while True:
            did_work = False
            for video_file in CalculateMetrics.VIDEO_FILES:
                for config in [True, False]:
                    X, y, current_idx, known_idx = get_design_space(
                        video_file, config, not config
                    )

            if not did_work:
                pass

        # with open("./config_declaration.yml", "rb") as f:
        #     config_hash = hashlib.md5(f.read()).hexdigest()

        # with open("./config_declaration.yml", "r", encoding="utf8") as f:
        #     config_declaration = get_config_declaration("", yaml.safe_load(f))
        #     f.seek(0)

        # config_options = [
        #     (k, get_config_options(i), i["type"])
        #     for k, i in config_declaration.items()
        #     if "skip_learn" not in i or not i["skip_learn"]
        # ]
        # X = np.array(np.meshgrid(*[c for _, c, _ in config_options])).T.reshape(
        #     -1, len(config_options)
        # )

        # requests = self._get_requests(config_hash)
        # while flatten(r for _, r in requests.items()):
        #     video_name, idx = self._get_request(requests)
        #     print(f"{video_name}: {idx}")

        #     # Remove the requested idx we are going to start work on.
        #     self._remove_requested_idx(video_name, idx, config_hash)

        #     self._set_config(idx, X, config_options)

        #     video_file = f"VISO/car/{video_name}"
        #     dataset_path = get_dataset_path(video_file)
        #     path = f"{dataset_path}/img"
        #     ground_truth_path = f"{dataset_path}/gt/gt.txt"

        #     MotionTrackerPipeline(path, runtime_config=self._runtime_config).run()
        #     SqliteParticleFilterPipeline(
        #         path, runtime_config=self._runtime_config
        #     ).run()

        #     recall, precision, f1 = self._get_metrics(
        #         "./output/results.db", ground_truth_path
        #     )

        #     self._set_known_idx(video_name, idx, config_hash, recall, precision, f1)
        #     self._save_results(video_name, idx, config_hash)

        #     # Update the requests in case more are running
        #     requests = self._get_requests(config_hash)
