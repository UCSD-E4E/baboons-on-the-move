"""
Blurs a gray frame using a Gaussian blur.
"""

import cv2
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.models.frame import Frame
from pipeline.decorators import stage
from pipeline import Stage


@stage("preprocessed_frame")
class BlurGray(Stage, PreprocessedFrameMixin):
    """
    Blurs a gray frame using a Gaussian blur.
    """

    def __init__(self, preprocessed_frame: PreprocessedFrameMixin):
        PreprocessedFrameMixin.__init__(self)
        Stage.__init__(self)

        self._preprocessed_frame = preprocessed_frame

    def execute(self) -> bool:
        """
        Blurs a gray frame using a Gaussian blur.
        """

        self.processed_frame = Frame(
            cv2.GaussianBlur(
                self._preprocessed_frame.processed_frame.get_frame(), (5, 5), 0
            ),
            self._preprocessed_frame.processed_frame.get_frame_number(),
        )

        return True
