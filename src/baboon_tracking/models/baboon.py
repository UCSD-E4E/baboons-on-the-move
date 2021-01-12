"""
Defines a baboon object.
"""
from typing import Tuple


class Baboon:
    """
    Defines a baboon object.
    """

    def __init__(self, centroid: Tuple[float, float], diameter: float):
        self.centroid = centroid
        self.diameter = diameter
