"""
Provides an algorithm for extracting baboons from drone footage.
"""
from typing import Dict
from baboon_tracking.stages.dead_reckoning import DeadReckoning
from baboon_tracking.stages.display_progress import DisplayProgress
from baboon_tracking.stages.draw_regions import DrawRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.motion_detector.motion_detector import MotionDetector
from baboon_tracking.stages.preprocess.preprocess_frame import PreprocessFrame
from baboon_tracking.stages.save_baboons import SaveBaboons

# from baboon_tracking.stages.save_video import SaveVideo
from baboon_tracking.stages.test_exit import TestExit
from pipeline import Serial
from pipeline.factory import factory
from pipeline.parent_stage import ParentStage
from pipeline.stage import Stage


from config import get_latest_config, set_config


preset_pipelines: Dict[str, Stage] = {}


def update_preset_pipelines(input_file="input.mp4", runtime_config=None):
    """
    Updates the input information for the preset pipelines.
    """

    ParentStage.static_stages = []

    preset_pipelines["default"] = Serial(
        "BaboonTracker",
        runtime_config,
        factory(GetVideoFrame, "./data/" + input_file),
        PreprocessFrame,
        MotionDetector,
        SaveBaboons,
        # DeadReckoning,
        DrawRegions,
        TestExit,
        DisplayProgress,
    )

    # config, _, _ = get_latest_config()
    # set_config(config)


update_preset_pipelines()
