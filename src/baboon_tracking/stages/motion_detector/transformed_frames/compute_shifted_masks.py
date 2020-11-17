import cv2
import numpy as np
from baboon_tracking.mixins.frame_mixin import FrameMixin

from baboon_tracking.mixins.shifted_masks_mixin import ShiftedMasksMixin
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from pipeline.decorators import stage
from pipeline.stage import Stage
from pipeline.stage_result import StageResult


@stage("transformation_matrices")
@stage("frame")
class ComputeShiftedMasks(Stage, ShiftedMasksMixin):
    def __init__(
        self, transformation_matrices: TransformationMatricesMixin, frame: FrameMixin
    ):
        ShiftedMasksMixin.__init__(self)
        Stage.__init__(self)

        self._transformation_matrices = transformation_matrices
        self._frame = frame

    def execute(self) -> StageResult:
        transformation_matrices = self._transformation_matrices.transformation_matrices
        frame = self._frame.frame

        img = np.ones(frame.get_frame().shape).astype(np.uint8)
        self.shifted_masks = [
            cv2.warpPerspective(
                img, M, (frame.get_frame().shape[1], frame.get_frame().shape[0]),
            )
            for M in transformation_matrices
        ]

        return StageResult(True, True)
