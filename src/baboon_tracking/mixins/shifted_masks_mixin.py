"""
Mixin for returning shifted masks.
"""


from typing import List

from baboon_tracking.models.frame import Frame


class ShiftedMasksMixin:
    """
    Mixin for returning shifted masks.
    """

    def __init__(self):
        self.shifted_masks: List[Frame] = []
