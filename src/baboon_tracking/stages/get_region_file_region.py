from typing import Any, Dict
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from library.region_file import RegionFile, region_factory
from pipeline import Stage
from pipeline.stage_result import StageResult
from baboon_tracking.decorators.debug import debug
from pipeline.decorators import stage
from pipeline.decorators import runtime_config


@debug(FrameMixin, (0, 255, 0))
@runtime_config("config")
@stage("frame")
class GetRegionFileRegion(Stage, BaboonsMixin):
    def __init__(self, frame: FrameMixin, config: Dict[str, Any]) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._frame = frame
        self._region_file: RegionFile = None

        if "region_file" in config:
            self._region_file = region_factory(config["region_file"])

    def execute(self) -> StageResult:
        self.baboons = list(
            self._region_file.frame_regions(self._frame.frame.get_frame_number())
        )

        return StageResult(True, True)
