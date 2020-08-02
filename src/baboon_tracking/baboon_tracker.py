"""
Provides an algorithm for extracting baboons from drone footage.
"""

from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.motion_detector.motion_detector import MotionDetector
from baboon_tracking.stages.preprocess.preprocess_frame import PreprocessFrame
from baboon_tracking.stages.test_exit import TestExit
from pipeline import Serial
from pipeline.factory import factory


class BaboonTracker:
    """
    An algorithm that attempts to extract baboons from drone footage.
    """

    def __init__(self):
        self._runner = Serial(
            "BaboonTracker",
            factory(GetVideoFrame, "./data/input.mp4"),
            PreprocessFrame,
            MotionDetector,
            TestExit,
        )

    def run(self):
        """
        Runs the algorithm until it finishes.
        """

        while True:
            # By reusing the state, we can store state between frames.
            success = self._runner.execute()

            if not success:
                return

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self._runner.flowchart()
        return img
