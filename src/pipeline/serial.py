"""
Implements a serial pipeline.
"""

from typing import Callable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw

from pipeline.parent_stage import ParentStage
from pipeline.stage_result import StageResult


class Serial(ParentStage):
    """
    A serial pipeline which can be used as a stage to provide a logical unit.
    """

    def __init__(self, name: str, *stage_types: List[Callable], runtime_config=None):
        ParentStage.__init__(self, name, *stage_types, runtime_config=runtime_config)

    def execute(self) -> StageResult:
        """
        Executes all stages in this pipeline sequentially.
        """

        result = None
        for stage in self.stages:
            stage.before_execute()
            result = stage.execute()
            stage.after_execute()

            if result.continue_pipeline and not result.next_stage:
                break

            if not result.continue_pipeline:
                return StageResult(False, None)

        should_continue = False
        if result is not None:
            should_continue = result.next_stage

        return StageResult(True, should_continue)

    def flowchart(self):
        """
        Generates a chart that represents this pipeline.
        """

        font = self._get_font(16)
        padding = np.array([10, 10])

        subcharts: List[Tuple[Image.Image, Tuple[int, int], Tuple[int, int]]] = [
            s.flowchart() for s in self.stages
        ]
        width = sum([img.size[0] for img, _, _ in subcharts]) + 20 * len(subcharts)

        max_img_height = max([img.size[1] for img, _, _ in subcharts])
        height = font.getsize(self.name)[1] + 20 + max_img_height

        img = Image.new("1", (width, height))
        draw = ImageDraw.Draw(img)

        self._draw_rectangle(img, draw)
        draw.text(self._array2tuple(padding - np.array([0, 1])), self.name, font=font)

        origin = np.array([10, font.getsize(self.name)[1] + 15])
        for i, subchart in enumerate(subcharts):
            sub, _, start = subchart
            height_pad = int((max_img_height - sub.size[1]) / 2)
            start = np.array(start) + np.array([0, height_pad])
            img.paste(sub, self._array2tuple(origin + np.array([0, height_pad])))

            if i != len(subcharts) - 1:
                next_sub, end, _ = subcharts[i + 1]
                next_height_pad = int((max_img_height - next_sub.size[1]) / 2)
                end = np.array(end) + np.array([0, next_height_pad])

                next_origin = origin + np.array([sub.size[0], 0]) + np.array([20, 0])

                start = self._array2tuple(start + np.array(origin))
                end = self._array2tuple(end + np.array(next_origin))

                draw.line([start, end], fill="black", width=2)

            origin += np.array([sub.size[0], 0]) + np.array([20, 0])

        start = self._array2tuple((0, img.size[1] / 2))
        end = self._array2tuple((img.size[0], img.size[1] / 2))

        return (img, start, end)
