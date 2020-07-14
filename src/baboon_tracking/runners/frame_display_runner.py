import cv2

from typing import Dict, Tuple
from ...runner import Runner


class FrameDisplayRunner(Runner):
    def __init__(self, window_title: str, image_key: str):
        Runner.__init__(self, "FrameDisplayRunner")

        self._window_title = window_title
        self._image_key = image_key

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        cv2.imshow(self._window_title, state[self._image_key])

        return (True, state)
