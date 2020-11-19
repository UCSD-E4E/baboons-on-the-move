from baboon_tracking.models.frame import Frame


class MovingForegroundMixin:
    def __init__(self):
        self.moving_foreground: Frame = None
