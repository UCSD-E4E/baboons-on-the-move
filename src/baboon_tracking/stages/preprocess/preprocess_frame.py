from .blur_gray import BlurGray
from .convert_from_bgr2gray import ConvertFromBGR2Gray
from ....pipeline import Serial


class PreprocessFrame(Serial):
    def __init__(self):
        Serial.__init__(self, "PreprocessFrame", ConvertFromBGR2Gray(), BlurGray())
