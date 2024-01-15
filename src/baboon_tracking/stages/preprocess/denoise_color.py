"""
Implements denoising using OpenCV.
"""
import cv2
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.frame_mixin import FrameMixin

from baboon_tracking.models.frame import Frame
from bom_pipeline import Stage
from bom_pipeline.stage_result import StageResult
from bom_pipeline.decorators import stage


@stage("frame")
@show_result
class DenoiseColor(Stage, FrameMixin):
    """
    Implements denoising using OpenCV.
    """

    def __init__(self, frame: FrameMixin) -> None:
        FrameMixin.__init__(self)
        Stage.__init__(self)

        self._frame = frame

    def execute(self) -> StageResult:
        self.frame = Frame(
            cv2.fastNlMeansDenoisingColored(
                self._frame.frame.get_frame(),
                h=3,
                hColor=20,
                templateWindowSize=7,
                searchWindowSize=21,
            ),
            self._frame.frame.get_frame_number(),
        )

        return StageResult(True, True)
