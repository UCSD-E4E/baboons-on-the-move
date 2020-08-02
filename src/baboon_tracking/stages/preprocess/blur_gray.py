"""
Blurs a gray frame using a Gaussian blur.
"""

from typing import Dict, Tuple
import cv2
from baboon_tracking.mixins.preprocessor_mixin import PreprocessorMixin
from pipeline import Stage
from baboon_tracking.models.frame import Frame


class BlurGray(Stage, PreprocessorMixin):
    """
    Blurs a gray frame using a Gaussian blur.
    """

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Blurs a gray frame using a Gaussian blur.
        """

        self.processed_frame = Frame(
            cv2.GaussianBlur(state["gray"].get_frame(), (5, 5), 0),
            state["gray"].get_frame_number(),
        )

        state["gray"].set_frame(cv2.GaussianBlur(state["gray"].get_frame(), (5, 5), 0))

        return (True, state)
