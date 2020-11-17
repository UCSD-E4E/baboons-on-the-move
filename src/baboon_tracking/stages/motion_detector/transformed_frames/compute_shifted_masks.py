from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from pipeline.decorators import stage
from pipeline.stage import Stage
from pipeline.stage_result import StageResult


@stage("transformation_matrices")
class ComputeShiftedMasks(Stage):
    def __init__(self, transformation_matrices: TransformationMatricesMixin):
        Stage.__init__(self)

        self.transformation_matrices = transformation_matrices

    def execute(self) -> StageResult:
        pass
