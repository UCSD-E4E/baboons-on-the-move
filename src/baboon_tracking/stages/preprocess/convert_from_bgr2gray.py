"""
Converts a color image to a gray-scale image.
"""
from typing import Dict, Tuple
import cv2
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.models.frame import Frame
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin

from pipeline import Stage
from pipeline.decorators import stage


@stage("frame_mixin")
class ConvertFromBGR2Gray(Stage, PreprocessedFrameMixin):
    """
    Converts a color image to a gray-scale image.
    """

    def __init__(self, frame_mixin: FrameMixin):
        PreprocessedFrameMixin.__init__(self)

        self._frame_mixin = frame_mixin

    def execute(self) -> bool:
        """
        Converts a color image to a gray-scale image.
        """

        self.processed_frame = Frame(
            cv2.cvtColor(self._frame_mixin.frame.get_frame(), cv2.COLOR_BGR2GRAY),
            self._frame_mixin.frame.get_frame_number(),
        )
        return True
