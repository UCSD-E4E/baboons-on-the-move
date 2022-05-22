"""
Plugin for calculating metrics.
"""
from argparse import ArgumentParser, Namespace
from datetime import datetime

import pandas as pd
import numpy as np
from firebase_admin import db

from cli_plugins.cli_plugin import CliPlugin
from library.firebase import initialize_app
from library.metrics import get_metrics
from config import get_latest_config, set_config
from sqlite3 import connect
from library.region import bb_intersection_over_union


class CalculateMetrics(CliPlugin):
    """
    Handles calculating metrics.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        self._connection = None
        self._cursor = None

    def execute(self, args: Namespace):
        """
        Calculate metrics for the specified video and output to Firebase.
        """
        file_name = "./output/results.db"

        self._connection = connect(file_name)
        self._cursor = self._connection.cursor()

        ground_truth = pd.read_csv("./data/gt.txt").to_numpy()
        found_regions = self._cursor.execute(
            "SELECT x1, y1, x2, y2, frame FROM motion_regions"
        )

        curr_frame = -1
        true_positive = 0
        false_negative = 0
        false_positive = 0
        truth = None
        for x1, y1, x2, y2, frame in found_regions:
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

            current = (x1, y1, x2, y2)
            matches = np.array([bb_intersection_over_union(current, t) for t in truth])

            if np.sum(matches) > 0:
                true_positive += 1
                truth = truth[np.logical_not(matches == np.max(matches))]
            else:
                false_positive += 1

        recall = true_positive / (false_negative + true_positive)
        precision = true_positive / (true_positive + false_positive)
        f1 = (2 * recall * precision) / (recall + precision)

        print(f"Recall: {recall}, Precision: {precision}, F1: {f1}")

        return

        initialize_app()
        config, _, _ = get_latest_config()
        set_config(config)

        time = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        ref = db.reference("metrics")
        video_ref = ref.child("input")
        date_ref = video_ref.child(time)

        date_ref.set(
            [
                {
                    "true_positive": m.true_positive,
                    "false_positive": m.false_positive,
                    "false_negative": m.false_negative,
                }
                for m in get_metrics()
            ]
        )

        latest_ref = video_ref.child("latest")
        latest_ref.set(time)

        # data_frame = pd.DataFrame(get_metrics())
        # data_frame.to_csv("input_metrics.csv")
