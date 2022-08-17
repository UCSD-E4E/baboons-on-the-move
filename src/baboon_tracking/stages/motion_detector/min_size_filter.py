"""
A filter that ensures blobs are of a minimum size.
"""
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.region import Region

from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage, config


@config("min_size", "motion_detector/min_size_filter/min_size")
@stage("baboons")
class MinSizeFilter(Stage, BaboonsMixin):
    """
    A filter that ensures blobs are of a minimum size.
    """

    def __init__(self, min_size: int, baboons: BaboonsMixin) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._min_size = min_size

        self._baboons = baboons

    def _calc_area(self, baboon: Region):
        x1, y1, x2, y2 = baboon.rectangle

        width = float(x2 - x1)
        height = float(y2 - y1)

        return width * height

    def execute(self) -> StageResult:
        self.baboons = [
            b for b in self._baboons.baboons if self._calc_area(b) >= self._min_size
        ]

        return StageResult(True, True)
