"""
Provides a super class for stages of a pipeline.
"""
from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


class Stage(ABC):
    """
    A stage of a pipeline.
    """

    def _array2tuple(self, array: np.array) -> Tuple[int, int]:
        return (array[0], array[1])

    def _draw_rectangle(self, img, draw):
        draw.rectangle(((0, 0), img.size), fill="white")
        draw.rectangle(
            ((0, 0), self._array2tuple(np.array(img.size) - np.array([1, 1]))),
            outline="black",
        )

    @abstractmethod
    def execute(self) -> bool:
        """
        When implemented in a child class, processes the provided state and returns a new state.
        """

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
