"Intersect frames to pull out the foreground."
import numpy as np
from baboon_tracking.mixins.intersected_frames_mixin import IntersectedFramesMixin
from baboon_tracking.mixins.group_shifted_history_frames_mixin import (
    GroupShiftedHistoryFramesMixin,
)

from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("group_shifted_history_frames")
class IntersectFrames(Stage, IntersectedFramesMixin):
    "Intersect frames to pull out the foreground."

    def __init__(
        self, group_shifted_history_frames: GroupShiftedHistoryFramesMixin
    ) -> None:
        Stage.__init__(self)
        IntersectedFramesMixin.__init__(self)
        self._group_shifted_history_frames = group_shifted_history_frames

    def execute(self) -> StageResult:
        grouped_shifted_history_frames = (
            self._group_shifted_history_frames.grouped_shifted_history_frames
        )
        grouped_quantized_frames = (
            self._group_shifted_history_frames.grouped_quantized_frames
        )

        self.intersected_frames = self._intersect_all_frames(
            grouped_shifted_history_frames, grouped_quantized_frames
        )

        return StageResult(True, True)

    def _intersect_frames(self, frames, q_frames):
        """
        Intersect two consecutive frames to find common background between those two frames
        Returns the single frame produced by intersection
        """
        mask = np.abs(q_frames[0] - q_frames[1]) <= 1
        combined = frames[0].get_frame().copy()
        combined[mask] = 0

        return combined

    def _intersect_all_frames(
        self, grouped_shifted_history_frames, grouped_quantized_frames
    ):
        """
        Takes in two lists of frames, performs intersect on each pair and returns array of intersects
        """
        return [
            self._intersect_frames(z[0], z[1])
            for z in zip(grouped_shifted_history_frames, grouped_quantized_frames)
        ]
