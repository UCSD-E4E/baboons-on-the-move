"""
Implements a dead reckoning filter to attempt to continue to track baboons.
"""

import pathlib
from typing import List
from math import sqrt
import shutil
from os.path import exists
import pickle

from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.models.baboon import Baboon
from library.region import bb_intersection_over_union
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import config, stage


flatten = lambda t: [item for sublist in t for item in sublist]


@config("dist_threshold", "dead_reckoning/dist_threshold")
@config("same_region_threshold", "dead_reckoning/same_region_threshold")
@stage("baboons")
@stage("frame")
class DeadReckoning(Stage, BaboonsMixin):
    """
    Implements a dead reckoning filter to attempt to continue to track baboons.
    """

    def __init__(
        self,
        dist_threshold: int,
        same_region_threshold: float,
        baboons: BaboonsMixin,
        frame: FrameMixin,
    ) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._dist_threshold = dist_threshold
        self._same_region_threshold = same_region_threshold

        self._baboons = baboons
        self._frame = frame

        self._counter = 0
        self._all_baboons = {}

        self._create_directory()

    def _create_directory(self):
        if exists("./temp/dead_reckoning"):
            shutil.rmtree("./temp/dead_reckoning")

        pathlib.Path("./temp").mkdir(exist_ok=True)
        pathlib.Path("./temp/dead_reckoning").mkdir(exist_ok=True)

    def _centroid(self, baboon: Baboon):
        x1, y1, x2, y2 = baboon.rectangle

        width = float(x2 - x1)
        height = float(y2 - y1)

        return (width / 2 + x1, height / 2 + y1)

    def _dist(self, first: Baboon, second: Baboon):
        first_center = self._centroid(first)
        second_center = self._centroid(second)

        return sqrt(
            (first_center[0] - second_center[0]) ** 2
            + (first_center[1] - second_center[1]) ** 2
        )

    def _calc_region_overlap(self, first: Baboon, second: Baboon):
        return bb_intersection_over_union(first.rectangle, second.rectangle)

    def _make_tuple(self, first: Baboon, second: Baboon, overlay: float):
        if first.identity is not None and second.identity is None:
            return (first, second, overlay)
        if first.identity is None and second.identity is not None:
            return (second, first, overlay)
        if first.identity is None and second.identity is None:
            return (first, second, overlay)

        id1 = min(first.identity, second.identity)
        if first.identity == id1:
            return (first, second, overlay)

        return (second, first, overlay)

    def has_frame(self, frame_number):
        """
        Checks if we have a list of baboons for the frame number.
        """
        return (frame_number in self._all_baboons) or exists(
            f"./temp/dead_reckoning/{frame_number}.pickle"
        )

    def get(self, frame_number: int) -> List[Baboon]:
        """
        Gets the list of baboons for the frame number.
        """
        if frame_number in self._all_baboons:
            return self._all_baboons[frame_number]

        file_path = f"./temp/dead_reckoning/{frame_number}.pickle"

        if exists(file_path):
            with open(file_path, "rb", encoding="utf8") as f:
                return pickle.load(f)

        raise IOError("Cannot find the specified frame number")

    def set(self, frame_number: int, baboons: List[Baboon]):
        """
        Sets the list of baboons for the frame number.
        """
        self._all_baboons[frame_number] = baboons

        if len(self._all_baboons) > 2:
            min_frame = min(self._all_baboons.keys())
            save = self._all_baboons.pop(min_frame)

            file_path = f"./temp/dead_reckoning/{min_frame}.pickle"

            with open(file_path, "wb") as f:
                pickle.dump(save, f)

    def execute(self) -> StageResult:
        prev_frame = self._frame.frame.get_frame_number() - 1
        baboons = self._baboons.baboons.copy()

        if self.has_frame(prev_frame):
            prev_baboons = self.get(prev_frame)

            distances = [
                [(p, b, self._dist(p, b)) for p in prev_baboons]
                for b in self._baboons.baboons
            ]
            distances = [
                [(p, b, d) for p, b, d in dist if d <= self._dist_threshold]
                for dist in distances
            ]
            distances = [d for d in distances if d]

            for dist in distances:
                dist.sort(key=lambda x: x[2])

            distances.sort(key=lambda x: x[0][2])
            while distances:
                dist_list = distances.pop(0)
                prev, curr, _ = dist_list.pop(0)

                curr.identity = prev.identity
                curr.id_str = prev.id_str

                for dist_list in distances:
                    for item in [
                        (p, b, d)
                        for p, b, d in dist_list
                        if curr.identity in (b.identity, p.identity)
                    ]:
                        dist_list.remove(item)

                    if not dist_list:
                        distances.remove(dist_list)

            prev_ids = {p.identity: p for p in prev_baboons}
            curr_ids = [b.identity for b in baboons if b.identity is not None]

            for id_str in curr_ids:
                if id_str in prev_ids:
                    prev_ids.pop(id_str)

            prev_items = [prev_ids[i] for i in prev_ids]

            baboons.extend(prev_items)

        baboon_regions = flatten(
            [
                [
                    (b1, b2, self._calc_region_overlap(b1, b2))
                    for b2 in baboons
                    if b1 != b2
                ]
                for b1 in baboons
            ]
        )
        same_baboons = {
            self._make_tuple(b1, b2, o)
            for b1, b2, o in baboon_regions
            if o >= self._same_region_threshold
        }

        for _, baboon, _ in same_baboons:
            if baboon in baboons:
                baboons.remove(baboon)

        for baboon in self._baboons.baboons:
            if baboon.identity is not None:
                continue

            baboon.id_str = str(self._counter)
            baboon.identity = self._counter
            self._counter += 1

        self.set(self._frame.frame.get_frame_number(), baboons)
        self.baboons = baboons

        return StageResult(True, True)
