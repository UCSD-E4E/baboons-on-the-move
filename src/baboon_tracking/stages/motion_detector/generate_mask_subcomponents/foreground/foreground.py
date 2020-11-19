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


class Foreground(Serial):
    def __init__(self) -> None:
        Serial.__init__(
            self,
            "Foreground",
            GroupFrames,
            IntersectFrames,
            UnionIntersections,
            SubtractBackground,
        )
