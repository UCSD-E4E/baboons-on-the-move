"""
Calculate the subcomponents that will later be combined into the moving foreground.
"""
from baboon_tracking.stages.motion_detector.generate_mask_subcomponents.foreground.foreground import (
    Foreground,
)
from baboon_tracking.stages.motion_detector.generate_mask_subcomponents.generate_history_of_dissimilarity import (
    GenerateHistoryOfDissimilarity,
)
from pipeline import Parallel


class GenerateMaskSubcomponents(Parallel):
    """
    Calculate the subcomponents that will later be combined into the moving foreground.
    """

    def __init__(self) -> None:
        Parallel.__init__(
            self,
            "GenerateMaskSubcomponents",
            GenerateHistoryOfDissimilarity,
            Foreground,
        )
