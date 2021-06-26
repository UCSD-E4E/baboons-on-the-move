"""
Provides a super class for stages of a pipeline.
"""
from abc import ABC, abstractmethod
from typing import Tuple
import os
import pathlib
import time
import urllib.request
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pipeline.models.time import Time
from pipeline.stage_result import StageResult


class Stage(ABC):
    """
    A stage of a pipeline.
    """

    def __init__(self):
        self._start = 0
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

    def _get_font(self, size: int):
        pathlib.Path("./tools").mkdir(exist_ok=True)

        url = "https://github.com/floriankarsten/space-grotesk/releases/download/2.0.0/SpaceGrotesk-2.0.0.zip"
        font_archive = "tools/SpaceGrotesk.zip"
        font_path = "tools/SpaceGrotesk"

        if not os.path.exists(font_archive):
            urllib.request.urlretrieve(url, font_archive)

        if not os.path.exists(font_path):
            archive = zipfile.ZipFile(font_archive, "r")

            archive.extractall(font_path)
            archive.close()

        return ImageFont.truetype(
            "tools/SpaceGrotesk/SpaceGrotesk-2.0.0/ttf/static/SpaceGrotesk-Regular.ttf",
            size,
        )

    def after_execute(self):
        """
        Executed after the execute method.
        """

        self._time += time.perf_counter() - self._start

    def before_execute(self):
        """
        Executed before the execute method.
        """

        self._start = time.perf_counter()
        self._executions += 1

    @abstractmethod
    def execute(self) -> StageResult:
        """
        When implemented in a child class, processes the provided state and returns a new state.
        """

    def on_init(self) -> None:
        """
        Called when the application is started.  Just before the pipeline begins.
        """

    def on_destroy(self) -> None:
        """
        Called when the application is closed, just before the pipeline is destroyed.
        """

    def get_time(self) -> Time:
        """
        Calculates the average time per execution of this stage.
        """

        return Time(type(self).__name__, self._time / self._executions)

    def flowchart_image(self):
        """
        Generates a flowchart for the current stage.
        """

        name = type(self).__name__

        font = self._get_font(24)

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
