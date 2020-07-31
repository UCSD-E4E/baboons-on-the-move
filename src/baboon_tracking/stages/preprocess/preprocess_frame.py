"""
Provides a pipeline step for preprocessing a frame.
"""

from baboon_tracking.stages.preprocess.blur_gray import BlurGray
from baboon_tracking.stages.preprocess.convert_from_bgr2gray import ConvertFromBGR2Gray
from pipeline import Serial


class PreprocessFrame(Serial):
    """
    Pipeline step for preprocessing a frame.
    """

    def __init__(self):
        Serial.__init__(self, "PreprocessFrame", ConvertFromBGR2Gray(), BlurGray())
