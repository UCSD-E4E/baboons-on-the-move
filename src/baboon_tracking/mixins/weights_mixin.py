"""
Mixin for returning weights.
"""

import numpy as np

from baboon_tracking.models.frame import Frame


class WeightsMixin:
    """
    Mixin for returning weights.
    """

    def __init__(self):
        self.weights: np.ndarray = np.array([])
        self.weights_frame: Frame = None
