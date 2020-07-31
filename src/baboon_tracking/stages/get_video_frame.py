"""
Get a video frame from a video file.
"""
from typing import Dict, Tuple
import cv2
from baboon_tracking.models.frame import Frame

from pipeline import Stage


class GetVideoFrame(Stage):
    """
    Get a video frame from a video file.
    """

    def __init__(self, video_path: str):
        Stage.__init__(self)

        self._capture = cv2.VideoCapture(video_path)
        self._frame_number = 1

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Get a video frame from a video file.
        """

        success, frame = self._capture.read()

        state["frame"] = Frame(frame, self._frame_number)
        self._frame_number += 1

        return (success, state)
