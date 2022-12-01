from library.region_file import RegionFile
from tqdm import tqdm
import pandas as pd
import numpy as np


class Metrics:
    def __init__(
        self,
        calculated: RegionFile,
        ground_truth: RegionFile,
        max_width: int = None,
        max_height: int = None,
        allow_overlap=False,
        threshold: float = 0,
    ):
        self._calculated = calculated
        self._ground_truth = ground_truth
        self._max_width = max_width
        self._max_height = max_height
        self._allow_overlap = allow_overlap
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

            selected_ground_regions = set()
            for c in calc:
                regions = [
                    (r, c.iou(r))
                    for r in gd
                    if r.identity not in selected_ground_regions
                ]
                regions = [(g, i) for g, i in regions if i > 0 and i >= self._threshold]

                if self._max_width is not None:
                    regions = [(g, i) for g, i in regions if g.width <= self._max_width]

                if self._max_height is not None:
                    regions = [
                        (g, i) for g, i in regions if g.height <= self._max_height
                    ]

                regions.sort(key=lambda x: x[1], reverse=True)
                ground_region = regions[0][0] if regions else None

                if not self._allow_overlap and ground_region:
                    selected_ground_regions.add(ground_region.identity)

                true_positive += 1 if ground_region else 0
                false_positive += 1 if not ground_region else 0

            selected_computed_region = set()
            for g in gd:
                regions = [
                    (r, g.iou(r))
                    for r in calc
                    if r.identity not in selected_computed_region
                ]
                regions = [(c, i) for c, i in regions if i > 0 and i >= self._threshold]

                if self._max_width is not None:
                    regions = [(g, i) for g, i in regions if g.width <= self._max_width]

                if self._max_height is not None:
                    regions = [
                        (g, i) for g, i in regions if g.height <= self._max_height
                    ]

                regions.sort(key=lambda x: x[1], reverse=True)
                computed_region = regions[0][0] if regions else None

                if not self._allow_overlap and computed_region:
                    selected_computed_region.add(computed_region.identity)

                false_negative += 1 if not computed_region else 0

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
