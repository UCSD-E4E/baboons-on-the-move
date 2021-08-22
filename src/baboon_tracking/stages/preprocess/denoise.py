"""
Implements denoising using OpenCV.
"""
import cv2

from baboon_tracking.models.frame import Frame
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage


@stage("preprocessed_frame")
class Denoise(Stage, PreprocessedFrameMixin):
    """
    Implements denoising using OpenCV.
    """

    def __init__(self, preprocessed_frame: PreprocessedFrameMixin) -> None:
        PreprocessedFrameMixin.__init__(self)
        Stage.__init__(self)

        self._preprocessed_frame = preprocessed_frame

    def execute(self) -> StageResult:
        self.processed_frame = Frame(
            cv2.fastNlMeansDenoising(
                self._preprocessed_frame.processed_frame.get_frame(), h=5
            ),
            self._preprocessed_frame.processed_frame.get_frame_number(),
        )

        return StageResult(True, True)
