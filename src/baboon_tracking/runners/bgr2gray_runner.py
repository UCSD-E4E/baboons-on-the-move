import cv2

from typing import Dict, Tuple
from ...runner.Runner import Runner


class BGR2GrayRunner(Runner):
    def __init__(self):
        Runner.__init__(self, "BGR2GrayRunner")

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        state["frame"].set_frame(
            cv2.cvtColor(state["frame"].get_frame(), cv2.COLOR_BGR2GRAY)
        )
        return (True, state)
