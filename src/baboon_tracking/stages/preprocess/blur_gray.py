"""
Blurs a gray frame using a Gaussian blur.
"""

from typing import Dict, Tuple
import cv2

from pipeline import Stage


class BlurGray(Stage):
    """
    Blurs a gray frame using a Gaussian blur.
    """

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Blurs a gray frame using a Gaussian blur.
        """

        state["gray"].set_frame(cv2.GaussianBlur(state["gray"].get_frame(), (5, 5), 0))

        return (True, state)
