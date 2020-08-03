"""
Tests for the press of the "Q" key or the end of the video.
"""

import cv2

from pipeline import Stage


class TestExit(Stage):
    """
    Tests for the press of the "Q" key or the end of the video.
    """

    def __init__(self) -> None:
        Stage.__init__(self)

    def execute(self) -> bool:
        """
        Tests for the press of the "Q" key or the end of the video.
        """

        if cv2.waitKey(25) & 0xFF == ord("q"):
            return False

        return True
