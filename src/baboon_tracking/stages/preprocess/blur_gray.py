import cv2

from typing import Dict, Tuple
from ....pipeline import Stage


class BlurGray(Stage):
    def execute(_, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        state["gray"] = cv2.GaussianBlur(state["gray"], (5, 5), 0)

        return (True, state)
