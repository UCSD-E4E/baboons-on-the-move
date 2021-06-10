"""
Executes child stages in parallel.
"""
from typing import Callable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw

from pipeline.parent_stage import ParentStage
from pipeline.stage_result import StageResult


class Parallel(ParentStage):
    """
    Executes child stages in parallel.
    """

    def __init__(self, name: str, *stage_types: List[Callable], runtime_config=None):
        ParentStage.__init__(self, name, *stage_types, runtime_config=runtime_config)

    def execute(self) -> StageResult:
        """
        Executes all stages in this pipeline in parallel.
        """

        for stage in self.stages:
            stage.before_execute()
            result = stage.execute()
            stage.after_execute()

            if result.continue_pipeline and not result.next_stage:
                break

            if not result.continue_pipeline:
                return StageResult(False, None)

        return StageResult(True, True)

    def flowchart(self):
        """
        Generates a chart that represents this pipeline.
        """

        font = self._get_font(16)
        padding = np.array([10, 10])

        subcharts: List[Tuple[Image.Image, Tuple[int, int], Tuple[int, int]]] = [
            s.flowchart() for s in self.stages
        ]
        height = (
            sum([img.size[1] for img, _, _ in subcharts])
            + 20 * len(subcharts)
            + font.getsize(self.name)[1]
        )

        max_img_width = max([img.size[0] for img, _, _ in subcharts])
        width = 20 + max_img_width

        img = Image.new("1", (width, height))
        draw = ImageDraw.Draw(img)

        self._draw_rectangle(img, draw)
        draw.text(self._array2tuple(padding - np.array([0, 1])), self.name, font=font)

        origin = np.array([10, font.getsize(self.name)[1] + 20])
        for subchart in subcharts:
            sub, _, start = subchart
            width_pad = int((max_img_width - sub.size[0]) / 2)
            start = np.array(start) + np.array([width_pad, 0])
            img.paste(sub, self._array2tuple(origin + np.array([width_pad, 0])))

            origin += np.array([0, sub.size[1]]) + np.array([0, 10])

        start = self._array2tuple((0, img.size[1] / 2))
        end = self._array2tuple((img.size[0], img.size[1] / 2))

        return (img, start, end)
