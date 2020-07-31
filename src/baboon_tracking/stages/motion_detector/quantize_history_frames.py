"""Quantizes the shifted history frame."""

from typing import Iterable, Dict, Tuple
import numpy as np
from baboon_tracking.models.frame import Frame
from pipeline.stage import Stage


class QuantizeHistoryFrames(Stage):
    """Quantizes the shifted history frame."""

    def __init__(self, scale_factor: float):
        Stage.__init__(self)

        self._scale_factor = scale_factor

    def _quantize_frame(self, frame: Frame):
        """
        Normalize pixel values from 0-255 to values from 0-self._scale_factor
        Returns quantized frame
        """
        return (
            np.floor(frame.get_frame().astype(np.float32) * self._scale_factor / 255.0)
            .astype(np.uint8)
            .astype(np.int32)
        )

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """Quantizes the shifted history frame."""
        shifted_history_frames: Iterable[Frame] = state["shifted_history_frames"]
        state["quantized_frames"] = [
            self._quantize_frame(f) for f in shifted_history_frames
        ]

        return (True, state)
