"""
Blurs a gray frame using a Gaussian blur.
"""

import cv2
from baboon_tracking.decorators.show import show
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.models.frame import Frame
from pipeline.decorators import stage, config
from pipeline import Stage
from pipeline.stage_result import StageResult


@show
@config(parameter_name="kernel_size", key="preprocess/kernel_size")
@stage("preprocessed_frame")
class BlurGray(Stage, PreprocessedFrameMixin):
    """
    Blurs a gray frame using a Gaussian blur.
    """

    def __init__(self, kernel_size: int, preprocessed_frame: PreprocessedFrameMixin):
        PreprocessedFrameMixin.__init__(self)
        Stage.__init__(self)

        self._kernel_size = kernel_size
        self._preprocessed_frame = preprocessed_frame

    def execute(self) -> StageResult:
        """
        Blurs a gray frame using a Gaussian blur.
        """

        self.processed_frame = Frame(
            cv2.GaussianBlur(
                self._preprocessed_frame.processed_frame.get_frame(),
                (self._kernel_size, self._kernel_size),
                0,
            ),
            self._preprocessed_frame.processed_frame.get_frame_number(),
        )

        return StageResult(True, True)
