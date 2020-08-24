"""
Implements a motion tracker pipeline.
"""

from baboon_tracking.stages.motion_detector.quantize_history_frames import (
    QuantizeHistoryFrames,
)
from baboon_tracking.stages.motion_detector.shift_history_frames import (
    ShiftHistoryFrames,
)
from baboon_tracking.stages.motion_detector.store_history_frame import StoreHistoryFrame
from pipeline import Serial


class MotionDetector(Serial):
    """
    Implements a motion tracker pipeline.
    """

    def __init__(self):
        Serial.__init__(
            self,
            "MotionDetector",
            StoreHistoryFrame,
            ShiftHistoryFrames,
            QuantizeHistoryFrames,
        )
