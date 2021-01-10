from typing import Tuple


class Baboon:
    def __init__(self, centroid: Tuple[float, float], diameter: float):
        self.centroid = centroid
        self.diameter = diameter
