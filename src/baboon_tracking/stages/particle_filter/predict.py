from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from pipeline import Stage

from pipeline.decorators import stage_from_previous_iteration
from pipeline.stage_result import StageResult


@stage_from_previous_iteration("baboons", is_property=True)
class Predict(Stage):
    def __init__(self) -> None:
        Stage.__init__(self)

        self._baboons: BaboonsMixin = None

    def execute(self) -> StageResult:
        return StageResult(True, True)

