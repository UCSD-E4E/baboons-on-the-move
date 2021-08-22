"""
Calculate the foreground of the current frame.
"""
from typing import Dict

from baboon_tracking.stages.motion_detector.generate_mask_subcomponents.foreground.group_frames import (
    GroupFrames,
)
from baboon_tracking.stages.motion_detector.generate_mask_subcomponents.foreground.intersect_frames import (
    IntersectFrames,
)
from baboon_tracking.stages.motion_detector.generate_mask_subcomponents.foreground.subtract_background import (
    SubtractBackground,
)
from baboon_tracking.stages.motion_detector.generate_mask_subcomponents.foreground.union_intersections import (
    UnionIntersections,
)
from pipeline import Serial
from pipeline.decorators import runtime_config


@runtime_config("rconfig")
class Foreground(Serial):
    """
    Calculate the foreground of the current frame.
    """

    def __init__(self, rconfig: Dict[str, any]) -> None:
        Serial.__init__(
            self,
            "Foreground",
            rconfig,
            GroupFrames,
            IntersectFrames,
            UnionIntersections,
            SubtractBackground,
        )
