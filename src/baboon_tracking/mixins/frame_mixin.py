from baboon_tracking.models.frame import Frame


class FrameMixin:
    def __init__(self):
        self.frame: Frame = None
