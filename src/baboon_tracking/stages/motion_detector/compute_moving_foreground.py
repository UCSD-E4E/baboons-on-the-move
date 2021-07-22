"""
Computes the moving foreground using the subcomponents previously computed
"""
import math
import numpy as np
from baboon_tracking.decorators.show_result import show_result

from baboon_tracking.mixins.foreground_mixin import ForegroundMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.history_of_dissimilarity_mixin import (
    HistoryOfDissimilarityMixin,
)
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.mixins.weights_mixin import WeightsMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import config, stage


@show_result
@stage("history_of_dissimilarity")
@stage("foreground")
@stage("weights")
@stage("frame_mixin")
@config(parameter_name="history_frames", key="motion_detector/history_frames")
class ComputeMovingForeground(Stage, MovingForegroundMixin):
    """
    Computes the moving foreground using the subcomponents previously computed
    """

    def __init__(
        self,
        history_of_dissimilarity: HistoryOfDissimilarityMixin,
        foreground: ForegroundMixin,
        weights: WeightsMixin,
        frame_mixin: FrameMixin,
        history_frames: int,
    ) -> None:
        Stage.__init__(self)
        MovingForegroundMixin.__init__(self)

        self._history_of_dissimilarity = history_of_dissimilarity
        self._foreground = foreground
        self._weights = weights
        self._frame = frame_mixin
        self._history_frames = history_frames

    def execute(self) -> StageResult:
        weights = self._weights.weights
        foreground = self._foreground.foreground
        history_of_dissimilarity = (
            self._history_of_dissimilarity.history_of_dissimilarity
        )

        self.moving_foreground = Frame(
            self._get_moving_foreground(weights, foreground, history_of_dissimilarity),
            self._frame.frame.get_frame_number(),
        )

        return StageResult(True, True)

    def _get_moving_foreground(self, weights, foreground, dissimilarity):
        """
        Calculates moving foreground according to figure 14 of paper
        Each of W and D (weights and dissimilarity) is assigned to high, medium, and low

        Medium commonality AND low commonality but low dissimiliarity are considered moving foreground
        Otherwise, it is either a still or flickering background

        Return frame representing moving foreground
        """

        history_frame_count_third = math.floor(float(self._history_frames - 1) / 3)
        third_gray = 255.0 / 3.0

        weights_low = (weights <= history_frame_count_third).astype(np.uint8)
        weights_medium = (
            np.logical_and(
                history_frame_count_third < weights, weights < self._history_frames - 1
            ).astype(np.uint8)
            * 2
        )

        weight_levels = weights_low + weights_medium

        foreground_low = (foreground <= math.floor(third_gray)).astype(np.uint8)
        foreground_medium = (
            (math.floor(third_gray) < foreground)
            + (foreground < math.floor(2 * third_gray))
        ).astype(np.uint8) * 2
        foreground_high = (foreground >= math.floor(2 * third_gray)).astype(
            np.uint8
        ) * 3

        foreground_levels = foreground_low + foreground_medium + foreground_high

        dissimilarity_low = (dissimilarity <= math.floor(third_gray)).astype(np.uint8)
        dissimilarity_medium = (
            (math.floor(third_gray) < dissimilarity)
            + (dissimilarity < math.floor(2 * third_gray))
        ).astype(np.uint8) * 2
        dissimilarity_high = (dissimilarity >= math.floor(2 * third_gray)).astype(
            np.uint8
        ) * 3

        dissimilarity_levels = (
            dissimilarity_low + dissimilarity_medium + dissimilarity_high
        )

        moving_foreground = np.logical_and(
            weight_levels == 2,
            np.greater_equal(foreground_levels, dissimilarity_levels),
        ).astype(np.uint8)
        moving_foreground = moving_foreground + np.logical_and(
            weight_levels == 1,
            np.logical_and(
                dissimilarity_levels == 1,
                np.greater(foreground_levels, dissimilarity_levels),
            ),
        ).astype(np.uint8)

        return moving_foreground * 255
