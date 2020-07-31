"""
Provides a super class for stages of a pipeline.
"""
from abc import ABC, abstractmethod
import time
from typing import Dict, Iterable, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


class Stage(ABC):
    """
    A stage of a pipeline.
    """

    def __init__(self):
        self._time = 0
        self._executions = 0

    def _array2tuple(self, array: np.array) -> Tuple[int, int]:
        return (array[0], array[1])

    def _draw_rectangle(self, img, draw):
        draw.rectangle(((0, 0), img.size), fill="white")
        draw.rectangle(
            ((0, 0), self._array2tuple(np.array(img.size) - np.array([1, 1]))),
            outline="black",
        )

    def before_execute(self):
        self._start = time.perf_counter()
        self._executions += 1

    def after_execute(self):
        self._time += time.perf_counter() - self._start

    @abstractmethod
    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        When implemented in a child class, processes the provided state and returns a new state.
        """

    def get_time(self) -> Iterable[Tuple[str, float]]:
        return [(type(self).__name__, self._time / self._executions)]

    def flowchart(self):
        """
        Generates a flowchart for the current stage.
        """

        name = type(self).__name__

        font = ImageFont.truetype("arial.ttf", 24)

        padding = np.array([10, 10])
        text_size = np.array(font.getsize(name))
        text_size_padding = text_size + 2 * padding

        img = Image.new("1", self._array2tuple(text_size_padding))
        draw = ImageDraw.Draw(img)

        self._draw_rectangle(img, draw)
        draw.text(self._array2tuple(padding - np.array([0, 1])), name, font=font)

        start = (0, img.size[1] / 2)
        end = (img.size[0], img.size[1] / 2)

        return (img, start, end)
