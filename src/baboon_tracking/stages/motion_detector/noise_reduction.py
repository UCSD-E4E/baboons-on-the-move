"""
Reduces the noise as a result of the motion detector.
"""
import cv2
import numpy as np
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.frame import Frame

from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage, config


@config(
    parameter_name="erode_kernel_size",
    key="motion_detector/noise_reduction/erode_kernel_size",
)
@config(
    parameter_name="dilate_kernel_size",
    key="motion_detector/noise_reduction/dilate_kernel_size",
)
@config(
    parameter_name="combine_kernel_size",
    key="motion_detector/noise_reduction/combine_kernel_size",
)
@stage("moving_foreground")
class NoiseReduction(Stage, MovingForegroundMixin):
    """
    Reduces the noise as a result of the motion detector.
    """

    def __init__(
        self,
        erode_kernel_size: int,
        dilate_kernel_size: int,
        combine_kernel_size: int,
        moving_foreground: MovingForegroundMixin,
    ) -> None:
        Stage.__init__(self)
        MovingForegroundMixin.__init__(self)

        self._erode_kernel_size = erode_kernel_size
        self._dilate_kernel_size = dilate_kernel_size
        self._combine_kernel_size = combine_kernel_size

        self._moving_foreground = moving_foreground

    def execute(self) -> StageResult:
        moving_foreground = self._moving_foreground.moving_foreground.get_frame()

        element = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (self._erode_kernel_size, self._erode_kernel_size)
        )
        eroded = cv2.erode(moving_foreground, element)

        element = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (self._dilate_kernel_size, self._dilate_kernel_size)
        )
        opened_mask = cv2.dilate(eroded, element)

        combined_mask = np.zeros(opened_mask.shape).astype(np.uint8)
        combined_mask[opened_mask == moving_foreground] = 255
        combined_mask[moving_foreground == 0] = 0

        element = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (self._combine_kernel_size, self._combine_kernel_size)
        )
        dialated = cv2.dilate(combined_mask, element)
        self.moving_foreground = Frame(
            cv2.erode(dialated, element),
            self._moving_foreground.moving_foreground.get_frame_number(),
        )

        return StageResult(True, True)
