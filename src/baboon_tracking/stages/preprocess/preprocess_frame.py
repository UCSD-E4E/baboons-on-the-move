"""
Provides a pipeline step for preprocessing a frame.
"""
from typing import Dict

from baboon_tracking.stages.preprocess.blur_gray import BlurGray
from baboon_tracking.stages.preprocess.convert_from_bgr2gray import ConvertFromBGR2Gray

# from baboon_tracking.stages.preprocess.feature_reduction_pca import FeatureReductionPca

# from baboon_tracking.stages.preprocess.denoise import Denoise
# from baboon_tracking.stages.preprocess.denoise_color import DenoiseColor
from bom_pipeline import Serial
from bom_pipeline.decorators import runtime_config


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
            # DenoiseColor,
            # FeatureReductionPca,
            ConvertFromBGR2Gray,
            # Denoise,
            BlurGray,
        )
