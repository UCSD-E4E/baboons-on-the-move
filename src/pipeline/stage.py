import numpy as np

from abc import ABC, abstractmethod
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Tuple


class Stage(ABC):
    def _array2tuple(self, array: np.array) -> Tuple[int, int]:
        return (array[0], array[1])

    @abstractmethod
    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        pass

    def flowchart(self):
        name = type(self).__name__

        font = ImageFont.truetype("arial.ttf", 24)

        padding = np.array([10, 10])
        text_size = np.array(font.getsize(name))
        text_size_padding = text_size + 2 * padding

        img = Image.new("1", self._array2tuple(text_size_padding))
        draw = ImageDraw.Draw(img)

        draw.rectangle(((0, 0), img.size), fill="white")
        draw.rectangle(
            ((0, 0), self._array2tuple(np.array(img.size) - np.array([1, 1]))),
            outline="black",
        )
        draw.text(self._array2tuple(padding - np.array([0, 1])), name, font=font)

        start = (0, img.size[1] / 2)
        end = (img.size[0], img.size[1] / 2)

        return (img, start, end)
