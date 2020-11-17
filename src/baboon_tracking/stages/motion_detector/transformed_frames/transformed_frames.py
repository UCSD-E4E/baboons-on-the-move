from baboon_tracking.stages.motion_detector.transformed_frames.compute_shifted_masks import (
    ComputeShiftedMasks,
)
from baboon_tracking.stages.motion_detector.transformed_frames.shift_history_frames import (
    ShiftHistoryFrames,
)
from pipeline.parallel import Parallel


class TransformedFrames(Parallel):
    def __init__(self):
        Parallel.__init__(
            self, "TransformedFrames", ShiftHistoryFrames, ComputeShiftedMasks
        )
