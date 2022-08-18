from typing import Dict, Iterator, List, Tuple
from ..baboon_tracking.models.region import Region
from library.region_file import RegionFile
from tqdm import tqdm


class Metrics:
    def __init__(
        self, calculated: RegionFile, ground_truth: RegionFile, threshold: float = 0
    ):
        self._calculated = calculated
        self._ground_truth = ground_truth
        self._threshold = threshold

    def calculate_metrics(self):
        true_positive = 0
        false_negative = 0
        false_positive = 0

        for calc, gd in tqdm(zip(self._calculated, self._ground_truth)):
            for c in calc:
                regions = [(r, c.iou(r)) for r in gd]
                regions = [(g, i) for g, i in regions if i > 0 and i >= self._threshold]

                true_positive += 1 if regions else 0
                false_positive += 1 if not regions else 0

            for g in gd:
                regions = [(r, g.iou(r)) for r in calc]
                regions = [(c, i) for c, i in regions if i > 0 and i >= self._threshold]

                false_negative += 1 if not regions else 0

        precision = true_positive / (true_positive + false_positive)
        recall = true_positive / (true_positive + false_negative)
        f1 = (2 * precision * recall) / (precision + recall)

        return recall, precision, f1
