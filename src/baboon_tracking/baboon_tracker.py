"""
Provides an algorithm for extracting baboons from drone footage.
"""
import time

from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.motion_detector.motion_detector import MotionDetector
from baboon_tracking.stages.preprocess.preprocess_frame import PreprocessFrame
from baboon_tracking.stages.show_frame import ShowFrame
from baboon_tracking.stages.test_exit import TestExit
from pipeline import Serial


class BaboonTracker:
    """
    An algorithm that attempts to extract baboons from drone footage.
    """

    def __init__(self):
        self._pipeline = Serial(
            "BaboonTracker",
            GetVideoFrame("./data/input.mp4"),
            PreprocessFrame(),
            MotionDetector(),
            ShowFrame("Gray", "gray"),
            TestExit(),
        )

    def run(self):
        """
        Runs the algorithm until it finishes.
        """

        state = {}
        start = time.perf_counter()
        iterations = 0
        while True:
            iterations += 1
            # By reusing the state, we can store state between frames.
            success, state = self._pipeline.execute(state)

            if not success:
                end = (time.perf_counter() - start) / iterations
                runtimes = self._pipeline.get_time()

                print("Total Time: " + str(end))
                print("Sum Total: " + str(sum([r for _, r in runtimes])))
                for name, runtime in runtimes:
                    print(name + ": " + str(runtime))

                return

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self._pipeline.flowchart()
        return img
