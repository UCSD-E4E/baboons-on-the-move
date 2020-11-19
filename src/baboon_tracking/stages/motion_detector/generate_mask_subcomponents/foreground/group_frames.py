from baboon_tracking.mixins.group_shifted_history_frames_mixin import (
    GroupShiftedHistoryFramesMixin,
)
from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from baboon_tracking.mixins.shifted_history_frames_mixin import (
    ShiftedHistoryFramesMixin,
)

from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("shifted_history_frames")
@stage("quantized_frames")
class GroupFrames(Stage, GroupShiftedHistoryFramesMixin):
    def __init__(
        self,
        shifted_history_frames: ShiftedHistoryFramesMixin,
        quantized_frames: QuantizedFramesMixin,
    ) -> None:
        Stage.__init__(self)
        GroupShiftedHistoryFramesMixin.__init__(self)

        self._shifted_history_frames = shifted_history_frames
        self._quantized_frames = quantized_frames

    def execute(self) -> StageResult:
        shifted_history_frames = self._shifted_history_frames.shifted_history_frames
        quantized_frames = self._quantized_frames.quantized_frames

        frame_group_index = range(len(shifted_history_frames) - 1)
        frame_group_index = [(r, r + 1) for r in frame_group_index]

        self.grouped_shifted_history_frames = [
            (shifted_history_frames[g[0]], shifted_history_frames[g[1]])
            for g in frame_group_index
        ]
        self.grouped_quantized_frames = [
            (quantized_frames[g[0]], quantized_frames[g[1]]) for g in frame_group_index
        ]

        return StageResult(True, True)

