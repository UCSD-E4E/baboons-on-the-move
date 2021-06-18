"""
Implements a stage which displays a progress bar.
"""

from typing import Dict
from tqdm import tqdm
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from pipeline import Stage
from pipeline.decorators import runtime_config, stage
from pipeline.stage_result import StageResult


@stage("capture")
@stage("frame")
@runtime_config("rconfig")
class DisplayProgress(Stage):
    """
    Implements a stage which displays a progress bar.
    """

    def __init__(
        self, rconfig: Dict[str, any], capture: CaptureMixin, frame: FrameMixin
    ) -> None:
        Stage.__init__(self)

        self._frame_count = int(capture.frame_count)
        self._progress = None
        self._frame = frame

        self._display_progress = True
        if "display_progress" in rconfig:
            self._display_progress = rconfig["display_progress"]

    def on_init(self) -> None:
        if not self._display_progress:
            return

        self._progress = tqdm(range(self._frame_count)).__iter__()

    def execute(self) -> StageResult:
        if not self._display_progress:
            return StageResult(True, True)

        idx = next(self._progress)

        while idx < self._frame.frame.get_frame_number():
            idx = next(self._progress)

        return StageResult(True, True)

    def on_destroy(self) -> None:
        if not self._display_progress:
            return

        self._progress.close()
