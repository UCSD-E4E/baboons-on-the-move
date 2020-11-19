import cv2
import numpy as np
from baboon_tracking.mixins.history_of_dissimilarity_mixin import (
    HistoryOfDissimilarityMixin,
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
class GenerateHistoryOfDissimilarity(Stage, HistoryOfDissimilarityMixin):
    def __init__(
        self,
        shifted_history_frames: ShiftedHistoryFramesMixin,
        quantized_frames: QuantizedFramesMixin,
    ) -> None:
        Stage.__init__(self)
        HistoryOfDissimilarityMixin.__init__(self)

        self._shifted_history_frames = shifted_history_frames
        self._quantized_frames = quantized_frames

    def execute(self) -> StageResult:
        shifted_history_frames = self._shifted_history_frames.shifted_history_frames
        quantized_frames = self._quantized_frames.quantized_frames

        self.history_of_dissimilarity = self._get_history_of_dissimilarity(
            shifted_history_frames, quantized_frames
        )

        return StageResult(True, True)

    def _get_history_of_dissimilarity(self, frames, q_frames):
        """
        Calculate history of dissimilarity according to figure 10 of paper
        Returns frame representing history of dissimilarity
        """
        dissimilarity = np.zeros(frames[0].get_frame().shape).astype(np.uint32)

        for i, _ in enumerate(frames):
            if i == 0:
                continue

            mask = (np.abs(q_frames[i] - q_frames[i - 1]) > 1).astype(np.uint32)
            dissimilarity = dissimilarity + np.multiply(
                np.abs(
                    frames[i].get_frame().astype(np.int32)
                    - frames[i - 1].get_frame().astype(np.int32)
                ),
                mask,
            )

        return (dissimilarity / len(frames)).astype(np.uint8)

