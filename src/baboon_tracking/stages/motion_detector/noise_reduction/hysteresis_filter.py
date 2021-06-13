"""
Implements a filter using Hysteriesis
"""
import numpy as np
from baboon_tracking.decorators.show import show

from baboon_tracking.models.frame import Frame
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from pipeline import Stage
from pipeline.decorators import stage, config
from pipeline.stage_result import StageResult


@show
@config(
    parameter_name="required_motion_observations",
    key="motion_detector/hysteresis/required_motion_observations",
)
@config(
    parameter_name="required_no_motion_observations",
    key="motion_detector/hysteresis/required_no_motion_observations",
)
@stage("moving_foreground")
class HysteresisFilter(Stage, MovingForegroundMixin):
    """
    Implements a filter using Hysteriesis
    """

    def __init__(
        self,
        required_motion_observations: int,
        required_no_motion_observations: int,
        moving_foreground: MovingForegroundMixin,
    ) -> None:
        Stage.__init__(self)
        MovingForegroundMixin.__init__(self)

        self._result = None
        self._motion_observations = None
        self._no_motion_observations = None
        self._required_motion_observations = required_motion_observations
        self._required_no_motion_observations = required_no_motion_observations
        self._moving_foreground = moving_foreground

    def execute(self) -> StageResult:
        if self._result is None:
            self._result = np.zeros_like(
                self._moving_foreground.moving_foreground.get_frame()
            )

            self._motion_observations = np.zeros_like(
                self._moving_foreground.moving_foreground.get_frame()
            )

            self._no_motion_observations = np.zeros_like(
                self._moving_foreground.moving_foreground.get_frame()
            )

        mask = self._moving_foreground.moving_foreground.get_frame() == 255
        not_mask = self._moving_foreground.moving_foreground.get_frame() == 0

        self._motion_observations[not_mask] = 0
        self._motion_observations[mask] += 1

        self._no_motion_observations[mask] = 0
        self._no_motion_observations[not_mask] += 1

        self._result[
            self._motion_observations == self._required_motion_observations
        ] = 255

        self._result[
            self._no_motion_observations == self._required_motion_observations
        ] = 0

        self.moving_foreground = Frame(
            self._result, self._moving_foreground.moving_foreground.get_frame_number()
        )

        return StageResult(True, True)
