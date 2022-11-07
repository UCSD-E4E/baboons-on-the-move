"""
Mixin for returning history of dissimilarity.
"""
import numpy as np

from baboon_tracking.models.frame import Frame


class HistoryOfDissimilarityMixin:
    """
    Mixin for returning history of dissimilarity.
    """

    def __init__(self):
        self.history_of_dissimilarity: np.ndarray = np.array([])
        self.history_of_dissimilarity_frame: Frame = None
