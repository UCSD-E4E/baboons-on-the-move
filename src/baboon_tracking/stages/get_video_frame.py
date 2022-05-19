"""
Get a video frame from a video file.
"""
from os.path import basename

import cv2

from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.models.frame import Frame

from pipeline.pipeline import Pipeline
from pipeline import Stage
from pipeline.stage_result import StageResult


class GetVideoFrame(Stage, FrameMixin, CaptureMixin):
    """
    Get a video frame from a video file.
    """

    def __init__(self, video_path: str):
        FrameMixin.__init__(self)
        CaptureMixin.__init__(self)
        Stage.__init__(self)

        # frame_count = self._get_frame_count(video_path)

        self._capture = cv2.VideoCapture(video_path)
        self.frame_width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self._capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = self._capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.name = basename(video_path)

        self._frame_number = 1

        Pipeline.iterations = self.frame_count

    def _get_frame_count(self, video_path: str):
        frame_count = 1

        cap = cv2.VideoCapture(video_path)
        success, _ = cap.read()
        while success:
            frame_count += 1
            success, _ = cap.read()

        return frame_count

    def execute(self) -> StageResult:
        """
        Get a video frame from a video file.
        """

        success, frame = self._capture.read()

        self.frame = Frame(frame, self._frame_number)
        self._frame_number += 1

        return StageResult(success, success)
