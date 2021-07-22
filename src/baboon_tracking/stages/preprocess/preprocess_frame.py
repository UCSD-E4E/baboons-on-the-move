"""
Provides a pipeline step for preprocessing a frame.
"""
from typing import Dict

from baboon_tracking.stages.preprocess.blur_gray import BlurGray
from baboon_tracking.stages.preprocess.convert_from_bgr2gray import ConvertFromBGR2Gray
from baboon_tracking.stages.preprocess.denoise_color import DenoiseColor

# from baboon_tracking.stages.preprocess.denoise import Denoise
from pipeline import Serial
from pipeline.decorators import runtime_config


@runtime_config("rconfig")
class PreprocessFrame(Serial):
    """
    Pipeline step for preprocessing a frame.
    """

    def __init__(self, rconfig: Dict[str, any]):
        Serial.__init__(
            self,
            "PreprocessFrame",
            rconfig,
            DenoiseColor,
            ConvertFromBGR2Gray,
            BlurGray,
            # Denoise,
        )
