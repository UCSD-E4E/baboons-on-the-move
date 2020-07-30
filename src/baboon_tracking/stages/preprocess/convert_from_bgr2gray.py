"""
Converts a color image to a gray-scale image.
"""
from typing import Dict, Tuple
import cv2

from pipeline import Stage


class ConvertFromBGR2Gray(Stage):
    """
    Converts a color image to a gray-scale image.
    """

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Converts a color image to a gray-scale image.
        """

        state["gray"] = cv2.cvtColor(state["frame"], cv2.COLOR_BGR2GRAY)
        return (True, state)
