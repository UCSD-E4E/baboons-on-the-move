"""
Mixin for returning history frames.
"""
from collections import deque
from typing import Deque
from baboon_tracking.models.frame import Frame


class HistoryFramesMixin:
    """
    Mixin for returning history frames.
    """

    def __init__(self, history_frame_count: int):
        self.history_frames: Deque[Frame] = deque([])

        self._history_frame_count = history_frame_count

    def is_full(self):
        """
        Returns true if the history frame deque is full.
        """
        return len(self.history_frames) >= self._history_frame_count
