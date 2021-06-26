from typing import Dict, List
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.baboon import Baboon
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("frame")
class GetCsvBaboon(Stage, BaboonsMixin):
    def __init__(self, frame: FrameMixin) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._frame = frame
        self._baboons_by_frame: Dict[int, List[Baboon]] = {}

    def on_init(self) -> None:
        with open("./data/baboons.csv", "r") as f:
            lines = [
                l.strip().split(", ") for i, l in enumerate(f.readlines()) if i != 0
            ]
            lines = [[int(p) for p in l] for l in lines]
            lines = [((l[0], l[1], l[2], l[3]), l[4]) for l in lines]

            for rect, frame_number in lines:
                if frame_number not in self._baboons_by_frame:
                    self._baboons_by_frame[frame_number] = []

                self._baboons_by_frame[frame_number].append(Baboon(rect))

    def execute(self) -> StageResult:
        frame_number = self._frame.frame.get_frame_number()

        if frame_number in self._baboons_by_frame:
            self.baboons = self._baboons_by_frame[frame_number]

            return StageResult(True, True)
        else:
            return StageResult(True, False)

