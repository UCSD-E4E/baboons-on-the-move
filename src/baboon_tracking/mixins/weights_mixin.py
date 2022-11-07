"""
Mixin for returning weights.
"""


from baboon_tracking.models.frame import Frame
import numpy as np


class WeightsMixin:
    """
    Mixin for returning weights.
    """

    def __init__(self):
        self.weights: np.ndarray = np.array([])
        self.weights_frame: Frame = None
