"""
Implements a stage that takes the input frame and draws the regions over it.
"""

import cv2
from baboon_tracking.decorators.show import show
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@show
@stage("frame")
@stage("baboons")
class DrawRegions(Stage):
    """
    Implements a stage that takes the input frame and draws the regions over it.
    """

    def __init__(self, frame: FrameMixin, baboons: BaboonsMixin) -> None:
        Stage.__init__(self)

        self._frame = frame
        self._baboons = baboons
        self.region_frame: Frame = None

    def execute(self) -> StageResult:
        region_frame = self._frame.frame.get_frame().copy()

        rectangles = [b.rectangle for b in self._baboons.baboons]
        for rect in rectangles:
            region_frame = cv2.rectangle(
                region_frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2
            )

        self.region_frame = Frame(region_frame, self._frame.frame.get_frame_number())

        return StageResult(True, True)
