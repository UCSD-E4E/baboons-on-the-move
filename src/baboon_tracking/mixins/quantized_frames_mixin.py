"""
Mixin for returning quantized frames.
"""
from typing import Iterable


class QuantizedFramesMixin:
    """
    Mixin for returning quantized frames.
    """

    def __init__(self):
        self.quantized_frames: Iterable = None
