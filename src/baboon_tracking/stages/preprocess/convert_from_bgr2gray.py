"""
Converts a color image to a gray-scale image.
"""
from typing import Dict, Tuple
import cv2
from baboon_tracking.models.frame import Frame

from pipeline import Stage


class ConvertFromBGR2Gray(Stage):
    """
    Converts a color image to a gray-scale image.
    """

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Converts a color image to a gray-scale image.
        """

        state["gray"] = Frame(
            cv2.cvtColor(state["frame"].get_frame(), cv2.COLOR_BGR2GRAY),
            state["frame"].get_frame_number(),
        )
        return (True, state)
