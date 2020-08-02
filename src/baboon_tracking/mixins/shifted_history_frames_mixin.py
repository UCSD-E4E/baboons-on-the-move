from typing import Iterable
from baboon_tracking.models.frame import Frame


class ShiftedHistoryFramesMixin:
    def __init__(self):
        self.shifted_history_frames: Iterable[Frame] = None
