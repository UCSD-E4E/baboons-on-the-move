"""
Implements a motion tracker pipeline.
"""

from pipeline import Serial
from .update_history_frame import UpdateHistoryFrame


class MotionDetector(Serial):
    """
    Implements a motion tracker pipeline.
    """

    def __init__(self):
        Serial.__init__(self, "MotionDetector", UpdateHistoryFrame(8))
