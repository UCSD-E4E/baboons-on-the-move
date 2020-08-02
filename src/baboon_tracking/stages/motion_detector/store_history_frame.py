"""
Implements a storage of historical frame step for motion detection.
"""

from baboon_tracking.mixins.history_frames_mixin import HistoryFramesMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from pipeline import Stage
from pipeline.decorators import config, stage


@config(parameter_name="history_frame_count", key="history_frames")
@stage("preprocessed_frame")
class StoreHistoryFrame(Stage, HistoryFramesMixin):
    """
    Implements a storage of historical frame step for motion detection.
    """

    def __init__(
        self, history_frame_count: int, preprocessed_frame: PreprocessedFrameMixin
    ):
        HistoryFramesMixin.__init__(self, history_frame_count)

        self._history_frame_count = history_frame_count
        self._preprocessed_frame = preprocessed_frame

    def execute(self) -> bool:
        """
        Implements a storage of historical frame step for motion detection.
        """
        if self.is_full():
            self.history_frames.popleft()

        self.history_frames.append(self._preprocessed_frame.processed_frame)

        return True
