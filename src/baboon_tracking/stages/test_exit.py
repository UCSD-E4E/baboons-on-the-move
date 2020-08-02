"""
Tests for the press of the "Q" key or the end of the video.
"""

from typing import Dict, Tuple
import cv2

from pipeline import Stage


class TestExit(Stage):
    """
    Tests for the press of the "Q" key or the end of the video.
    """

    def __init__(self) -> None:
        Stage.__init__(self)

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Tests for the press of the "Q" key or the end of the video.
        """

        if cv2.waitKey(25) & 0xFF == ord("q"):
            return (False, state)

        return (True, state)
