"""
Implements a stage which shifts history frames.
"""
import cv2
import numpy as np
from baboon_tracking.mixins.history_frames_mixin import HistoryFramesMixin
from baboon_tracking.mixins.shifted_history_frames_mixin import (
    ShiftedHistoryFramesMixin,
)
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from baboon_tracking.models.frame import Frame
from pipeline.decorators import stage
from pipeline.stage import Stage
from pipeline.stage_result import StageResult


@stage("transformation_matrices")
@stage("history_frames")
class ShiftHistoryFrames(Stage, ShiftedHistoryFramesMixin):
    """
    Implements a stage which shifts history frames.
    """

    def __init__(
        self,
        history_frames: HistoryFramesMixin,
        transformation_matrices: TransformationMatricesMixin,
    ):
        ShiftedHistoryFramesMixin.__init__(self)
        Stage.__init__(self)

        self._history_frames = history_frames
        self._transformation_matrices = transformation_matrices

    def execute(self) -> StageResult:
        """
        Registers the history frame.
        """

        history_frames = self._history_frames.history_frames

        transformation_matrices = self._transformation_matrices.transformation_matrices

        self.shifted_history_frames = [
            Frame(
                cv2.warpPerspective(
                    history_frame.get_frame(),
                    M,
                    (
                        history_frame.get_frame().shape[1],
                        history_frame.get_frame().shape[0],
                    ),
                ).astype(np.uint8),
                history_frame.get_frame_number(),
            )
            for history_frame, M in zip(history_frames, transformation_matrices)
        ]

        return StageResult(True, True)
