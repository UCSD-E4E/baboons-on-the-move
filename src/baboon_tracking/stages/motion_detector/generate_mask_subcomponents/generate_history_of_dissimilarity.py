"""
Generate the history of dissimilarity
"""

import cv2
import numpy as np
from baboon_tracking.decorators.save_img_result import save_img_result
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.history_of_dissimilarity_mixin import (
    HistoryOfDissimilarityMixin,
)
from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from baboon_tracking.mixins.shifted_history_frames_mixin import (
    ShiftedHistoryFramesMixin,
)
from library.utils import scale_ndarray

from bom_pipeline import Stage
from bom_pipeline.decorators import stage
from bom_pipeline.stage_result import StageResult


@stage("shifted_history_frames")
@stage("quantized_frames")
@stage("frame")
@save_img_result
class GenerateHistoryOfDissimilarity(Stage, HistoryOfDissimilarityMixin):
    """
    Generate the history of dissimilarity
    """

    def __init__(
        self,
        shifted_history_frames: ShiftedHistoryFramesMixin,
        quantized_frames: QuantizedFramesMixin,
        frame: FrameMixin,
    ) -> None:
        Stage.__init__(self)
        HistoryOfDissimilarityMixin.__init__(self)

        self._shifted_history_frames = shifted_history_frames
        self._quantized_frames = quantized_frames
        self._frame = frame

    def execute(self) -> StageResult:
        shifted_history_frames = self._shifted_history_frames.shifted_history_frames
        quantized_frames = self._quantized_frames.quantized_frames

        self.history_of_dissimilarity = self._get_history_of_dissimilarity(
            shifted_history_frames, quantized_frames
        )
        self.history_of_dissimilarity_frame = scale_ndarray(
            self.history_of_dissimilarity, self._frame.frame.get_frame_number()
        )

        return StageResult(True, True)

    def _get_history_of_dissimilarity(self, frames, q_frames):
        """
        Calculate history of dissimilarity according to figure 10 of paper
        Returns frame representing history of dissimilarity
        """
        dissimilarity = np.zeros(frames[0].get_frame().shape, dtype=np.uint32)

        for i, _ in enumerate(frames):
            if i == 0:
                continue

            mask = np.abs(q_frames[i] - q_frames[i - 1]) <= 1
            dissimilarity_part = cv2.absdiff(
                frames[i].get_frame(), frames[i - 1].get_frame()
            )
            dissimilarity_part[mask] = 0
            dissimilarity += dissimilarity_part

        return (dissimilarity / len(frames)).astype(np.uint8)
