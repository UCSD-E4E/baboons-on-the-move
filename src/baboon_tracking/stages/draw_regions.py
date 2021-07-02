"""
Implements a stage that takes the input frame and draws the regions over it.
"""

import cv2
from baboon_tracking.decorators.save_result import save_result
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@save_result
@show_result
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

        if self._baboons.baboons:
            rectangles = [(b.rectangle, b.id_str) for b in self._baboons.baboons]
            for rect, id_str in rectangles:
                region_frame = cv2.rectangle(
                    region_frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2
                )

                if id_str is not None:
                    cv2.putText(
                        region_frame,
                        id_str,
                        (rect[0], rect[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (36, 255, 12),
                        2,
                    )

        self.region_frame = Frame(region_frame, self._frame.frame.get_frame_number())

        return StageResult(True, True)
