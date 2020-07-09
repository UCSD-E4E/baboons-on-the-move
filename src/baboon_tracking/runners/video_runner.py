import cv2

from typing import Dict, Tuple
from ..models import Frame
from ...runner import Runner


class VideoRunner(Runner):
    def __init__(self, video_path: str):
        Runner.__init__(self, "VideoRunner")

        self._capture = cv2.VideoCapture(video_path)
        self._frame_number = 1

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        success, frame = self._capture.read()

        result = (success, {"frame": Frame(frame, self._frame_number)})
        self._frame_number += 1

        return result
