"""
Implements a storage of historical frame step for motion detection.
"""

from collections import deque
from typing import Deque, Dict, Tuple
from baboon_tracking.models.frame import Frame
from pipeline import Stage


class StoreHistoryFrame(Stage):
    """
    Implements a storage of historical frame step for motion detection.
    """

    def __init__(self, history_frame_count: int):
        Stage.__init__(self)

        self._history_frame_count = history_frame_count

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Implements a storage of historical frame step for motion detection.
        """
        if "history_frames" not in state:
            state["history_frames"] = deque([])

        # Allow for autocomplete.
        history_frames: Deque[Frame] = state["history_frames"]

        if "history_full" in state and state["history_full"]:
            history_frames.popleft()

        history_frames.append(state["gray"])
        state["history_full"] = len(history_frames) >= self._history_frame_count

        return (True, state)
