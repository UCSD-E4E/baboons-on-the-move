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

        self._frame_count = int(capture.frame_count)
        self._progress = None
        self._frame = frame

    def on_init(self) -> None:
        self._progress = tqdm(range(self._frame_count)).__iter__()

    def execute(self) -> StageResult:
        idx = next(self._progress)

        while idx < self._frame.frame.get_frame_number():
            idx = next(self._progress)

        return StageResult(True, True)

    def on_destroy(self) -> None:
        self._progress.close()
