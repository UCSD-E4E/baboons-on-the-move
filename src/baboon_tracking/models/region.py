"""
Defines a region object.
"""
from typing import Tuple
from typing_extensions import Self
from library.region import bb_intersection_over_union


class Region:
    """
    Defines a region object.
    """

    def __init__(
        self,
        rectange: Tuple[int, int, int, int],
        id_str: str = None,
        identity: int = None,
    ):
        self.rectangle = rectange
        self.id_str = id_str
        self.identity = identity

    def iou(self, other: Self):
        return bb_intersection_over_union(self.rectangle, other.rectangle)
