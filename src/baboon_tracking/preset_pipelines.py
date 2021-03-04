"""
Provides an algorithm for extracting baboons from drone footage.
"""
from typing import Dict
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.motion_detector.motion_detector import MotionDetector
from baboon_tracking.stages.preprocess.preprocess_frame import PreprocessFrame
from baboon_tracking.stages.save_video import SaveVideo
from baboon_tracking.stages.test_exit import TestExit
from pipeline import Serial
from pipeline.factory import factory
from pipeline.parent_stage import ParentStage
from pipeline.stage import Stage


preset_pipelines: Dict[str, Stage] = {}


def update_preset_pipelines(input_file="input.mp4"):
    """
    Updates the input information for the preset pipelines.
    """

    ParentStage.static_stages = []

    preset_pipelines["default"] = Serial(
        "BaboonTracker",
        factory(GetVideoFrame, "./data/" + input_file),
        PreprocessFrame,
        MotionDetector,
        SaveVideo,
        TestExit,
    )


update_preset_pipelines()
