from pipeline import Stage
from pipeline.stage_result import StageResult


class Resample(Stage):
    def __init__(self) -> None:
        Stage.__init__(self)

    def execute(self) -> StageResult:
        return StageResult(True, True)

