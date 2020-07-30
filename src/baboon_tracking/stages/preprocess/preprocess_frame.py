"""
Provides a pipeline step for preprocessing a frame.
"""

from pipeline import Serial

from .blur_gray import BlurGray
from .convert_from_bgr2gray import ConvertFromBGR2Gray


class PreprocessFrame(Serial):
    """
    Pipeline step for preprocessing a frame.
    """

    def __init__(self):
        Serial.__init__(self, "PreprocessFrame", ConvertFromBGR2Gray(), BlurGray())
