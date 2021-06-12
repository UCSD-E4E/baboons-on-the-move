"""
Implements a group filter to ensure that all pixels are in a group at least size n.
"""

from typing import Tuple
import numpy as np
from numba import jit, prange
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.decorators import config, stage
from pipeline.stage_result import StageResult


@jit(nopython=True)
def _pixel_has_neighbors(moving_foreground, group_size: int, coord: Tuple[int, int]):
    x_coord, y_coord = coord

    height, width = moving_foreground.shape

    if moving_foreground[y_coord, x_coord] == 0:
        return False

    min_x = max(x_coord - 1, 0)
    max_x = min(x_coord + 1, width - 1)

    min_y = max(y_coord - 1, 0)
    max_y = min(y_coord + 1, height - 1)

    count = 0
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if y == y_coord and x == x_coord:
                continue

            if moving_foreground[y, x] > 0:
                count += 1

            if count >= group_size:
                return True

    return False


@jit(nopython=True, parallel=True)
# @cuda.jit()
def _execute(
    moving_foreground, curr_moving_foreground, group_size: int, height: int, width: int
):
    for y in prange(height):
        for x in prange(width):
            if _pixel_has_neighbors(curr_moving_foreground, group_size, (x, y),):
                moving_foreground[y, x] = 255


@config("group_size", "motion_detector/group_filter/size")
@stage("moving_foreground")
class GroupFilter(Stage, MovingForegroundMixin):
    """
    Implements a group filter to ensure that all pixels are in a group at least size n.
    """

    def __init__(
        self, group_size: int, moving_foreground: MovingForegroundMixin
    ) -> None:
        Stage.__init__(self)
        MovingForegroundMixin.__init__(self)

        self._group_size = group_size
        self._moving_foreground = moving_foreground

    def execute(self) -> StageResult:
        moving_foreground = np.zeros_like(
            self._moving_foreground.moving_foreground.get_frame()
        )
        height, width = moving_foreground.shape

        # _execute[5, 256](
        #     moving_foreground,
        #     self._moving_foreground.moving_foreground.get_frame(),
        #     self._group_size,
        #     height,
        #     width,
        # )

        _execute(
            moving_foreground,
            self._moving_foreground.moving_foreground.get_frame(),
            self._group_size,
            height,
            width,
        )

        self.moving_foreground = Frame(
            moving_foreground,
            self._moving_foreground.moving_foreground.get_frame_number(),
        )

        return StageResult(True, True)
