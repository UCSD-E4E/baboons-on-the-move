from baboon_tracking.models.frame import Frame


class PreprocessedFrameMixin:
    def __init__(self):
        self.processed_frame: Frame = None
