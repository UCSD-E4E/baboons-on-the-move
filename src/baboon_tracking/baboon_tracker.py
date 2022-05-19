"""
Provides an algorithm for extracting baboons from drone footage.
"""
from pipeline.pipeline import Pipeline
from baboon_tracking.stages.display_progress import DisplayProgress
from baboon_tracking.stages.draw_regions import DrawRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.motion_detector.motion_detector import MotionDetector
from baboon_tracking.stages.overlay import Overlay
from baboon_tracking.stages.preprocess.preprocess_frame import PreprocessFrame
from baboon_tracking.stages.save_baboons import SaveBaboons
from baboon_tracking.stages.test_exit import TestExit
from pipeline.factory import factory


class BaboonTracker(Pipeline):
    """
    An algorithm that attempts to extract baboons from drone footage.
    """

    def __init__(self, input_file: str, runtime_config=None):
        Pipeline.__init__(
            self,
            "BaboonTracker",
            factory(GetVideoFrame, "./data/" + input_file),
            PreprocessFrame,
            MotionDetector,
            SaveBaboons,
            Overlay,
            DrawRegions,
            TestExit,
            # DisplayProgress,
            runtime_config=runtime_config,
        )

    def flowchart_image(self):
        """
        Generates a chart representing the algorithm.
        """

        (
            img,
            _,
            _,
        ) = self.stage.flowchart_image()
        return img
