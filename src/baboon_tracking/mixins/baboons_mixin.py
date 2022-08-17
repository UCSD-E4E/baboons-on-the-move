"""
Mixin for returning baboon objects.
"""

from typing import List

from baboon_tracking.models.region import Region


class BaboonsMixin:
    """
    Mixin for returning baboon objects.
    """

    def __init__(self):
        self.baboons: List[Region] = None
