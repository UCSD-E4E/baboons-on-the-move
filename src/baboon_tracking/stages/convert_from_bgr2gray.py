import cv2

from typing import Dict, Tuple
from ...pipeline import Stage


class ConvertFromBGR2Gray(Stage):
    def execute(_, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        state["gray"] = cv2.cvtColor(state["frame"], cv2.COLOR_BGR2GRAY)
        return (True, state)
