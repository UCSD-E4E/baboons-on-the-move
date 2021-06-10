"""
Provides a pipeline step for preprocessing a frame.
"""

from baboon_tracking.stages.preprocess.blur_gray import BlurGray
from baboon_tracking.stages.preprocess.convert_from_bgr2gray import ConvertFromBGR2Gray

# from baboon_tracking.stages.preprocess.denoise import Denoise
from baboon_tracking.stages.show_last_frame import ShowLastFrame
from pipeline import Serial
from pipeline.decorators import runtime_config


@runtime_config("rconfig")
class PreprocessFrame(Serial):
    """
    Pipeline step for preprocessing a frame.
    """

    def __init__(self, rconfig=None):
        Serial.__init__(
            self,
            "PreprocessFrame",
            ConvertFromBGR2Gray,
            BlurGray,
            # Denoise,
            ShowLastFrame,
            runtime_config=rconfig,
        )
