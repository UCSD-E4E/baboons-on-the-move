"""
Implements a stage which displays a progress bar.
"""

from tqdm import tqdm
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("capture")
@stage("frame")
class DisplayProgress(Stage):
    """
    Implements a stage which displays a progress bar.
    """

    def __init__(self, capture: CaptureMixin, frame: FrameMixin) -> None:
        Stage.__init__(self)

        self._progress = tqdm(range(int(capture.frame_count))).__iter__()
        self._frame = frame

    def execute(self) -> StageResult:
        idx = next(self._progress)

        while idx < self._frame.frame.get_frame_number():
            idx = next(self._progress)

        return StageResult(True, True)
