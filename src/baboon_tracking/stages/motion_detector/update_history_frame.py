from collections import deque
from typing import Deque, Dict, Tuple
from ....pipeline import Stage


class UpdateHistoryFrame(Stage):
    def __init__(self, history_frame_count: int):
        self._history_frame_count = history_frame_count

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        if "history_frames" not in state:
            state["history_frames"] = deque([])

        # Allow for autocomplete.
        history_frames: Deque = state["history_frames"]

        if len(history_frames) >= self._history_frame_count:
            history_frames.popleft()

        history_frames.append(state["gray"])

        return (True, state)
