from typing import Dict, Tuple
import cv2

from ...runner import Runner


class CheckForExitRunner(Runner):
    def __init__(self):
        Runner.__init__(self, "CheckForExitRunner")

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        if cv2.waitKey(25) & 0xFF == ord("q"):
            return (False, state)

        return (True, state)
