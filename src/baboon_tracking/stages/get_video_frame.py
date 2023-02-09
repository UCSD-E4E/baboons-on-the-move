"""
Get a video frame from a video file.
"""
from os import listdir
from os.path import basename, isdir

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

        self._files = None
        self._video_path = video_path

        self._is_video_file = self._get_is_video(video_path)

        self.name = None
        if self._is_video_file:
            self._init_video_file(video_path)
        else:
            self._init_image_directory(video_path)

        if self.name is None:
            self.name = basename(video_path)

        self._frame_number = 1

        Pipeline.iterations = self.frame_count

    def _get_is_video(self, video_path: str):
        return not isdir(video_path)

    def _init_video_file(self, video_path: str):
        self._capture = cv2.VideoCapture(video_path)
        self.frame_width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self._capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = self._capture.get(cv2.CAP_PROP_FRAME_COUNT)

    def _init_image_directory(self, video_path: str):
        self._files = listdir(video_path)
        self._files.sort()

        img = cv2.imread(f"{video_path}/{self._files[0]}")
        self.frame_height, self.frame_width, _ = img.shape
        self.fps = 30
        self.frame_count = len(self._files)

        if "data/Datasets/" in video_path:
            parts = video_path.split("/")
            idx = parts.index("Datasets")

            self.name = "/".join(parts[(idx + 1) : -1])

    def execute(self) -> StageResult:
        """
        Get a video frame from a video file.
        """

        if self._is_video_file:
            result = self._execute_video_file()
        else:
            result = self._execute_image_directory()

        return result

    def _execute_video_file(self) -> StageResult:
        success, frame = self._capture.read()

        self.frame = Frame(frame, self._frame_number)
        self._frame_number += 1

        return StageResult(success, success)

    def _execute_image_directory(self) -> StageResult:
        frame = cv2.imread(f"{self._video_path}/{self._files[self._frame_number - 1]}")

        self.frame = Frame(frame, self._frame_number)
        self._frame_number += 1

        return StageResult(self._frame_number <= self.frame_count, True)
