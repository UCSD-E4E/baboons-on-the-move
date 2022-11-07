"""
Mixin for returning the foreground.
"""


from baboon_tracking.models.frame import Frame


class ForegroundMixin:
    """
    Mixin for returning the foreground.
    """

    def __init__(self):
        self.foreground: Frame = None
