import cv2

from typing import Dict, Tuple
from ...runner import Runner


class FrameDisplayRunner(Runner):
    def __init__(self, window_title: str):
        Runner.__init__(self, "FrameDisplayRunner")

        self._window_title = window_title

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        cv2.imshow(self._window_title, state["frame"].get_frame())

        return (True, state)
