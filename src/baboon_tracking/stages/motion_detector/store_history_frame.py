"""
Implements a storage of historical frame step for motion detection.
"""

from rx.subject import Subject
from baboon_tracking.mixins.history_frames_mixin import HistoryFramesMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from pipeline import Stage
from pipeline.decorators import config, stage
from pipeline.stage_result import StageResult


@config(
    parameter_name="history_frame_count",
    key="motion_detector/history_frames",
)
@stage("preprocessed_frame")
class StoreHistoryFrame(Stage, HistoryFramesMixin):
    """
    Implements a storage of historical frame step for motion detection.
    """

    def __init__(
        self, history_frame_count: int, preprocessed_frame: PreprocessedFrameMixin
    ):
        self._history_frame_popped_subject = Subject()
        self.history_frame_popped = self._history_frame_popped_subject

        HistoryFramesMixin.__init__(
            self, history_frame_count, self.history_frame_popped
        )
        Stage.__init__(self)

        self._history_frame_count = history_frame_count
        self._preprocessed_frame = preprocessed_frame
        self._next_history_frame = None

    def execute(self) -> StageResult:
        """
        Implements a storage of historical frame step for motion detection.
        """
        if self.is_full():
            frame = self.history_frames.popleft()
            self._history_frame_popped_subject.on_next(frame)

        if self._next_history_frame is not None:
            self.history_frames.append(self._next_history_frame)

        self._next_history_frame = self._preprocessed_frame.processed_frame

        return StageResult(True, True)
