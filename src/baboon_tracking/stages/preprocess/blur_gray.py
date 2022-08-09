"""
Blurs a gray frame using a Box blur.
"""

import cv2
import numpy as np
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.models.frame import Frame
from pipeline.decorators import stage, config
from pipeline import Stage
from pipeline.stage_result import StageResult


@show_result
@config(parameter_name="kernel_size", key="preprocess/kernel_size")
@stage("preprocessed_frame")
class BlurGray(Stage, PreprocessedFrameMixin):
    """
    Blurs a gray frame using a Box blur.
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

        kernel = np.ones((self._kernel_size, self._kernel_size), np.float32) / (
            self._kernel_size**2
        )
        self.processed_frame = Frame(
            cv2.filter2D(
                self._preprocessed_frame.processed_frame.get_frame(), -1, kernel
            ),
            self._preprocessed_frame.processed_frame.get_frame_number(),
        )

        return StageResult(True, True)
