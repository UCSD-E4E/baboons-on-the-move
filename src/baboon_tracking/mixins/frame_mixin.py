"""
Mixin for returning frames.
"""
from baboon_tracking.models.frame import Frame


class FrameMixin:
    """
    Mixin for returning frames.
    """

    def __init__(self):
        self.frame: Frame = None
