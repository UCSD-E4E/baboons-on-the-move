"""
Get an image frame from a directory
"""
import os
import cv2

from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.stage_result import StageResult


class GetImgFrame(Stage, FrameMixin, CaptureMixin):
    """
    Get an image frame from a directory
    """

    def __init__(self) -> None:
        FrameMixin.__init__(self)
        CaptureMixin.__init__(self)
        Stage.__init__(self)

        self._directory = "./data/img"
        self._files = os.listdir(self._directory)
        self._files.sort()

        img = cv2.imread(self._directory + "/" + self._files[0])
        self.frame_width, self.frame_height, _ = img.shape
        self.fps = 30
        self.frame_count = len(self._files)
        self.name = "img"

        self._frame_number = 1

    def execute(self) -> StageResult:
        frame = cv2.imread(self._directory + "/" + self._files[self._frame_number - 1])

        self.frame = Frame(frame, self._frame_number)
        self._frame_number += 1

        return StageResult(self._frame_number <= self.frame_count, True)
