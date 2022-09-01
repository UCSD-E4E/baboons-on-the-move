from baboon_tracking.mixins.frame_mixin import FrameMixin
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage

from baboon_tracking.decorators.show_result import show_result


@stage("frame")
@show_result
class RepeatVideoFrame(Stage):
    def __init__(self, frame: FrameMixin) -> None:
        Stage.__init__(self)

        self._frame = frame

    def execute(self) -> StageResult:
        self.frame = self._frame.frame

        return StageResult(True, True)
