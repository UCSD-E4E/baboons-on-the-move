"""
Provides an algorithm for extracting baboons from drone footage.
"""

from pipeline import Serial

from .stages.motion_detector.motion_detector import MotionDetector
from .stages.preprocess.preprocess_frame import PreprocessFrame
from .stages import GetVideoFrame, ShowFrame, TestExit


class BaboonTracker:
    """
    An algorithm that attempts to extract baboons from drone footage.
    """

    def __init__(self):
        self._runner = Serial(
            "BaboonTracker",
            GetVideoFrame("./data/input.mp4"),
            PreprocessFrame(),
            MotionDetector(),
            TestExit(),
        )

    def run(self):
        """
        Runs the algorithm until it finishes.
        """

        state = {}
        while True:
            # By reusing the state, we can store state between frames.
            success, state = self._runner.execute(state)

            if not success:
                return

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self._runner.flowchart()
        return img
