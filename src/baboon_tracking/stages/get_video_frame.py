"""
Get a video frame from a video file.
"""
import cv2
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.models.frame import Frame

from pipeline import Stage


class GetVideoFrame(Stage, FrameMixin):
    """
    Get a video frame from a video file.
    """

    def __init__(self, video_path: str):
        FrameMixin.__init__(self)
        Stage.__init__(self)

        self._capture = cv2.VideoCapture(video_path)
        self._frame_number = 1

    def execute(self) -> bool:
        """
        Get a video frame from a video file.
        """

        success, frame = self._capture.read()

        self.frame = Frame(frame, self._frame_number)
        self._frame_number += 1

        return success
