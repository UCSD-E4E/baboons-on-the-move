"""
Mixin for returning shifted history frames.
"""
from typing import Iterable
from baboon_tracking.models.frame import Frame


class ShiftedHistoryFramesMixin:
    """
    Mixin for returning shifted history frames.
    """

    def __init__(self):
        self.shifted_history_frames: Iterable[Frame] = None
