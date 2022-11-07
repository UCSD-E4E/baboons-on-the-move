from library.region_file import RegionFile
from tqdm import tqdm
import pandas as pd
import numpy as np


class Metrics:
    def __init__(
        self, calculated: RegionFile, ground_truth: RegionFile, threshold: float = 0
    ):
        self._calculated = calculated
        self._ground_truth = ground_truth
        self._threshold = threshold

    def calculate_metrics(self):
        df = pd.DataFrame(
            columns=["frame", "true_positive", "false_negative", "false_positive"]
        )

        for calc, gd in tqdm(zip(self._calculated, self._ground_truth)):
            if self._calculated.current_frame != self._ground_truth.current_frame:
                raise "The frame numbers don't match"

            true_positive = 0
            false_negative = 0
            false_positive = 0

            calc = list(calc)
            gd = list(gd)

            for c in calc:
                regions = [(r, c.iou(r)) for r in gd]
                regions = [(g, i) for g, i in regions if i > 0 and i >= self._threshold]

                true_positive += 1 if regions else 0
                false_positive += 1 if not regions else 0

            for g in gd:
                regions = [(r, g.iou(r)) for r in calc]
                regions = [(c, i) for c, i in regions if i > 0 and i >= self._threshold]

                false_negative += 1 if not regions else 0

            df.loc[len(df.index)] = [
                self._calculated.current_frame,
                true_positive,
                false_negative,
                false_positive,
            ]

        true_positive = df["true_positive"].sum()
        false_negative = df["false_negative"].sum()
        false_positive = df["false_positive"].sum()

        precision = 0
        recall = 0
        f1 = 0

        if true_positive + false_positive != 0:
            precision = true_positive / (true_positive + false_positive)
        if true_positive + false_negative != 0:
            recall = true_positive / (true_positive + false_negative)
        if precision + recall != 0:
            f1 = (2 * precision * recall) / (precision + recall)

        return recall, precision, f1, df
