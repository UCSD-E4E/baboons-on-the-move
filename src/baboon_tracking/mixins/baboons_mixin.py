from typing import List

from baboon_tracking.models.baboon import Baboon


class BaboonsMixin:
    def __init__(self):
        self.baboons: List[Baboon] = None
