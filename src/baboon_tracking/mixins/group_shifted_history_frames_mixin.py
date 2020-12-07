"""
Mixin for returning the groups of shifted history frames.
"""


class GroupShiftedHistoryFramesMixin:
    """
    Mixin for returning the groups of shifted history frames.
    """

    def __init__(self):
        self.grouped_shifted_history_frames = []
        self.grouped_quantized_frames = []
