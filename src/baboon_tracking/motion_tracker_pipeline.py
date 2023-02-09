"""
Provides an algorithm for extracting motion regions from drone footage.
"""
from pipeline.pipeline import Pipeline
from pipeline.factory import factory

from baboon_tracking.decorators.debug import DisplayDebugRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.motion_detector.motion_detector import MotionDetector
from baboon_tracking.stages.overlay import Overlay
from baboon_tracking.stages.preprocess.preprocess_frame import PreprocessFrame
from baboon_tracking.stages.save_motion_regions import SaveMotionRegions
from baboon_tracking.stages.test_exit import TestExit


class MotionTrackerPipeline(Pipeline):
    """
    An algorithm that attempts to extract motion regions from drone footage.
    """

    def __init__(self, video_path: str, runtime_config=None):
        Pipeline.__init__(
            self,
            "MotionTrackerPipeline",
            factory(GetVideoFrame, video_path),
            PreprocessFrame,
            MotionDetector,
            SaveMotionRegions,
            Overlay,
            DisplayDebugRegions,
            TestExit,
            runtime_config=runtime_config,
        )
