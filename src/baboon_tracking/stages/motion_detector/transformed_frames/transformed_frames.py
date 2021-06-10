"""
Transforms frames using previously computed transformation matrix.
"""

from baboon_tracking.stages.motion_detector.transformed_frames.compute_shifted_masks import (
    ComputeShiftedMasks,
)
from baboon_tracking.stages.motion_detector.transformed_frames.shift_history_frames import (
    ShiftHistoryFrames,
)
from pipeline.parallel import Parallel
from pipeline.decorators import runtime_config


@runtime_config("rconfig")
class TransformedFrames(Parallel):
    """
    Transforms frames using previously computed transformation matrix.
    """

    def __init__(self, rconfig=None):
        Parallel.__init__(
            self,
            "TransformedFrames",
            ShiftHistoryFrames,
            ComputeShiftedMasks,
            runtime_config=rconfig,
        )
