from typing import Iterable


class QuantizedFramesMixin:
    def __init__(self):
        self.quantized_frames: Iterable = None
