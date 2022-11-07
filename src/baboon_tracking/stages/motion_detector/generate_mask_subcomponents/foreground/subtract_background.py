"""
Subtracts background representation from the frame.
"""

import cv2
from baboon_tracking.decorators.save_img_result import save_img_result
from baboon_tracking.mixins.foreground_mixin import ForegroundMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.mixins.unioned_frames_mixin import UnionedFramesMixin
from baboon_tracking.mixins.weights_mixin import WeightsMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.decorators import config, stage
from pipeline.stage_result import StageResult


@stage("preprocessed_frame")
@stage("unioned_frames")
@stage("weights")
@stage("frame")
@config(parameter_name="history_frames", key="motion_detector/history_frames")
@save_img_result
class SubtractBackground(Stage, ForegroundMixin):
    """
    Subtracts background representation from the frame.
    """

    def __init__(
        self,
        preprocessed_frame: PreprocessedFrameMixin,
        unioned_frames: UnionedFramesMixin,
        weights: WeightsMixin,
        frame: FrameMixin,
        history_frames: int,
    ) -> None:
        Stage.__init__(self)
        ForegroundMixin.__init__(self)

        self._preprocessed_frame = preprocessed_frame
        self._unioned_frames = unioned_frames
        self._weights = weights
        self._frame = frame
        self._history_frames = history_frames

    def execute(self) -> StageResult:
        frame = self._preprocessed_frame.processed_frame
        union = self._unioned_frames.unioned_frames
        weights = self._weights.weights

        frame_new = self._zero_weights(frame.get_frame(), weights)
        union_new = self._zero_weights(union, weights)

        self.foreground = Frame(
            cv2.absdiff(frame_new, union_new), self._frame.frame.get_frame_number()
        )

        return StageResult(True, True)

    def _zero_weights(self, frame, weights):
        """
        Gets foreground of frame by zeroing out all pixels with large weights,
        i.e. pixels in which frequency of commonality
        is really high, meaning that it hasn't changed much or at all in the
        history frames, according to figure 13 of paper
        Returns frame representing the foreground
        """
        f = frame.copy()
        f[weights >= self._history_frames - 1] = 0

        return f
