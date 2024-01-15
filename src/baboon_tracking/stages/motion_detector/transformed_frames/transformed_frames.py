"""
Transforms frames using previously computed transformation matrix.
"""
from typing import Dict

from baboon_tracking.stages.motion_detector.transformed_frames.compute_shifted_masks import (
    ComputeShiftedMasks,
)
from baboon_tracking.stages.motion_detector.transformed_frames.shift_history_frames import (
    ShiftHistoryFrames,
)
from bom_pipeline.parallel import Parallel
from bom_pipeline.decorators import runtime_config


@runtime_config("rconfig")
class TransformedFrames(Parallel):
    """
    Transforms frames using previously computed transformation matrix.
    """

    def __init__(self, rconfig: Dict[str, any]):
        Parallel.__init__(
            self,
            "TransformedFrames",
            rconfig,
            ShiftHistoryFrames,
            ComputeShiftedMasks,
        )
