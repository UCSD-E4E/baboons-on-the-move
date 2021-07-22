from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("baboons")
@stage("frame")
class SaveBaboons(Stage):
    def __init__(self, baboons: BaboonsMixin, frame: FrameMixin) -> None:
        Stage.__init__(self)

        self._baboons = baboons
        self._frame = frame
        self._file = open("./output/baboons.csv", "w")
        self._file.write("x1, y1, x2, y2, frame\n")

    def execute(self) -> StageResult:
        for baboon in self._baboons.baboons:
            x1, y1, x2, y2 = baboon.rectangle

            self._file.write(str(x1))
            self._file.write(", ")
            self._file.write(str(y1))
            self._file.write(", ")
            self._file.write(str(x2))
            self._file.write(", ")
            self._file.write(str(y2))
            self._file.write(", ")
            self._file.write(str(self._frame.frame.get_frame_number()))
            self._file.write("\n")

        return StageResult(True, True)

    def on_destroy(self) -> None:
        self._file.close()
