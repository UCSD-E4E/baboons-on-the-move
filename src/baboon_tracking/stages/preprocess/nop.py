from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("frame_mixin")
class Nop(Stage, PreprocessedFrameMixin):
    def __init__(self, frame_mixin: FrameMixin) -> None:
        Stage.__init__(self)
        PreprocessedFrameMixin.__init__(self)

        self._frame_mixin = frame_mixin

    def execute(self) -> StageResult:
        self.processed_frame = self._frame_mixin.frame

        return StageResult(True, True)

