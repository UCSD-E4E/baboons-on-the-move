"""
Applies the masks to the moving foreground.
"""

import numpy as np
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.mixins.shifted_masks_mixin import ShiftedMasksMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage


@stage("moving_foreground")
@stage("shifted_masks")
@stage("frame")
class ApplyMasks(Stage, MovingForegroundMixin):
    """
    Applies the masks to the moving foreground.
    """

    def __init__(
        self,
        moving_foreground: MovingForegroundMixin,
        shifted_masks: ShiftedMasksMixin,
        frame: FrameMixin,
    ) -> None:
        Stage.__init__(self)
        MovingForegroundMixin.__init__(self)

        self._moving_foreground = moving_foreground
        self._shifted_masks = shifted_masks
        self._frame = frame

    def execute(self) -> StageResult:
        # This cleans up the edges after performing image registration.
        for mask in self._shifted_masks.shifted_masks:
            self.moving_foreground = Frame(
                np.multiply(
                    self._moving_foreground.moving_foreground.get_frame(), mask
                ),
                self._frame.frame.get_frame_number(),
            )

        return StageResult(True, True)
