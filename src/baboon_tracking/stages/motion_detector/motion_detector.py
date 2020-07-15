from .update_history_frame import UpdateHistoryFrame
from ....pipeline import Serial


class MotionDetector(Serial):
    def __init__(self):
        Serial.__init__(self, "MotionDetector", UpdateHistoryFrame(8))
