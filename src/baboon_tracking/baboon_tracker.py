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
        self._pipeline = Serial(
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
            self._pipeline.before_execute()
            result = self._pipeline.execute()
            self._pipeline.after_execute()

            if not result.continue_pipeline:
                print("Average Runtime per stage:")
                self._pipeline.get_time().print_to_console()

                return

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self._pipeline.flowchart()
        return img
