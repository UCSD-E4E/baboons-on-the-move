"""
Reduces the noise as a result of the motion detector.
"""
import cv2
import numpy as np
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.frame import Frame

from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage


@stage("moving_foreground")
class NoiseReduction(Stage, MovingForegroundMixin):
    """
    Reduces the noise as a result of the motion detector.
    """

    def __init__(self, moving_foreground: MovingForegroundMixin) -> None:
        Stage.__init__(self)
        MovingForegroundMixin.__init__(self)

        self._moving_foreground = moving_foreground

    def execute(self) -> StageResult:
        moving_foreground = self._moving_foreground.moving_foreground.get_frame()

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        eroded = cv2.erode(moving_foreground, element)

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30))
        opened_mask = cv2.dilate(eroded, element)

        combined_mask = np.zeros(opened_mask.shape).astype(np.uint8)
        combined_mask[opened_mask == moving_foreground] = 255
        combined_mask[moving_foreground == 0] = 0

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12))
        dialated = cv2.dilate(combined_mask, element)
        self.moving_foreground = Frame(
            cv2.erode(dialated, element),
            self._moving_foreground.moving_foreground.get_frame_number(),
        )

        return StageResult(True, True)
