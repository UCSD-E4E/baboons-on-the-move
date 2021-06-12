from typing import Dict
from baboon_tracking.stages.motion_detector.dilate_erode_filter import DilateErodeFilter
from baboon_tracking.stages.motion_detector.group_filter import GroupFilter
from baboon_tracking.stages.motion_detector.hysteresis_filter import HysteresisFilter
from pipeline import ConfigSerial
from pipeline.decorators import runtime_config
from pipeline.stage_result import StageResult


@runtime_config("rconfig")
class NoiseReduction(ConfigSerial):
    def __init__(self, rconfig: Dict[str, any]) -> None:
        ConfigSerial.__init__(
            self,
            "NoiseReduction",
            "motion_detector_stages",
            rconfig,
            HysteresisFilter,
            GroupFilter,
            DilateErodeFilter,
        )

