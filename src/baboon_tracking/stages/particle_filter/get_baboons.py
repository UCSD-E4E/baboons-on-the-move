from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin


@stage("baboons")
class GetBaboons(Stage, BaboonsMixin):
    def __init__(self, baboons: BaboonsMixin) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._baboons = baboons

    def execute(self) -> StageResult:
        self.baboons = self._baboons.baboons.copy()

        return StageResult(True, True)

