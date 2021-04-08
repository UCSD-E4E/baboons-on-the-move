"""Quantizes the shifted history frame."""

import numpy as np
import math
from numba import vectorize
from baboon_tracking.mixins.shifted_history_frames_mixin import (
    ShiftedHistoryFramesMixin,
)
from baboon_tracking.models.frame import Frame
from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from pipeline.decorators import config, stage
from pipeline.stage import Stage
from pipeline.stage_result import StageResult


@vectorize("i4(u1, i8)", nopython=True, target="cpu", cache=True)
def vector_quantize(value, scale_factor):
    """
    pointwise quantize operation for numba vectorization
    """
    return math.floor(value * scale_factor /255.0)


@config(parameter_name="scale_factor", key="quantize_frames/scale_factor")
@stage("shifted_history_frames")
class QuantizeHistoryFrames(Stage, QuantizedFramesMixin):
    """Quantizes the shifted history frame."""

    def __init__(
        self, scale_factor: float, shifted_history_frames: ShiftedHistoryFramesMixin
    ):
        QuantizedFramesMixin.__init__(self)
        Stage.__init__(self)

        self._scale_factor = scale_factor
        self._shifted_history_frames = shifted_history_frames

    def _quantize_frame(self, frame: Frame):
        """
        Normalize pixel values from 0-255 to values from 0-self._scale_factor
        Returns quantized frame
        """
        return np.floor(
            frame.get_frame().astype(np.float32) * self._scale_factor / 255.0
        ).astype(np.int32)

    def execute(self) -> StageResult:
        """Quantizes the shifted history frame."""
        #self._shifted_history_frames.shifted_history_frames_list = [f.get_frame() for f in self._shifted_history_frames.shifted_history_frames]
        self.quantized_frames = [
            vector_quantize(f.get_frame(), self._scale_factor) for f in self._shifted_history_frames.shifted_history_frames
        ]

        return StageResult(True, True)
