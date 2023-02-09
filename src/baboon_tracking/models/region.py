"""
Defines a region object.
"""
from typing import Tuple
from typing_extensions import Self

from library.region import bb_intersection_over_union


class Point:
    """
    Defines a single point object.
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


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
        x1, y1, x2, y2 = rectange
        self.top_left = Point(x1, y1)
        self.bottom_right = Point(x2, y2)

        self.id_str = id_str
        self.identity = identity

    @property
    def rectangle(self) -> Tuple[int, int, int, int]:
        return (
            self.top_left.x,
            self.top_left.y,
            self.bottom_right.x,
            self.bottom_right.y,
        )

    @property
    def width(self) -> int:
        return self.bottom_right.x - self.top_left.x

    @property
    def height(self) -> int:
        return self.bottom_right.y - self.top_left.y

    def iou(self, other: Self):
        return bb_intersection_over_union(self.rectangle, other.rectangle)
