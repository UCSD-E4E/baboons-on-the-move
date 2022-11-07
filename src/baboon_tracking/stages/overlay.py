"""
Creates a video overlaying the blobs over the original video.
"""
import numpy as np

from baboon_tracking.decorators.save_video_result import save_video_result
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@show_result
@save_video_result
@stage("frame")
@stage("moving_foreground")
class Overlay(Stage):
    """
    Creates a video overlaying the blobs over the original video.
    """

    def __init__(
        self, frame: FrameMixin, moving_foreground: MovingForegroundMixin
    ) -> None:
        Stage.__init__(self)

        self._frame = frame
        self._moving_foreground = moving_foreground
        self.overlay_frame: Frame = None

    def execute(self) -> StageResult:
        frame = self._frame.frame
        moving_foreground = self._moving_foreground.moving_foreground

        scaled_foreground = moving_foreground.get_frame().astype(np.float32) / 255
        scaled_foreground[scaled_foreground == 0] = 0.5
        scaled_foreground = np.tile(scaled_foreground, (3, 1, 1))
        scaled_foreground = np.swapaxes(scaled_foreground, 0, 1)
        scaled_foreground = np.swapaxes(scaled_foreground, 1, 2)

        self.overlay_frame = Frame(
            (frame.get_frame() * scaled_foreground).astype(np.uint8),
            frame.get_frame_number(),
        )

        return StageResult(True, True)
