"""
Tests for the press of the "Q" key or the end of the video.
"""

import cv2

from pipeline import Stage
from pipeline.stage_result import StageResult


class TestExit(Stage):
    """
    Tests for the press of the "Q" key or the end of the video.
    """

    def __init__(self) -> None:
        Stage.__init__(self)

    def execute(self) -> StageResult:
        """
        Tests for the press of the "Q" key or the end of the video.
        """

        if cv2.waitKey(50) & 0xFF == ord("q"):
            return StageResult(False, None)

        return StageResult(True, True)
