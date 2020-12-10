"""
Provides an algorithm for extracting baboons from drone footage.
"""
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.motion_detector.motion_detector import MotionDetector
from baboon_tracking.stages.preprocess.preprocess_frame import PreprocessFrame
from baboon_tracking.stages.test_exit import TestExit
from pipeline import Serial
from pipeline.factory import factory


preset_pipelines = {}


preset_pipelines["default"] = Serial(
    "BaboonTracker",
    factory(GetVideoFrame, "./data/input.mp4"),
    PreprocessFrame,
    MotionDetector,
    TestExit,
)

preset_pipelines["travis_test"] = Serial(
    "BaboonTrackerTravisTest",
    factory(GetVideoFrame, "./data/input.mp4"),
    PreprocessFrame,
    MotionDetector,
    TestExit,
)

preset_pipelines["headless"] = Serial(
    "Headless",
    factory(GetVideoFrame, "./data/input.mp4"),
    PreprocessFrame,
    MotionDetector,
    TestExit,
)
