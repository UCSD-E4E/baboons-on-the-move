"""
Mixin for returning baboon objects.
"""

from typing import List

from baboon_tracking.models.baboon import Baboon


class BaboonsMixin:
    """
    Mixin for returning baboon objects.
    """

    def __init__(self):
        self.baboons: List[Baboon] = None
