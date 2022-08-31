from pipeline.pipeline import Pipeline
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.test_exit import TestExit
from pipeline.factory import factory


class DatasetViewerPipeline(Pipeline):
    def __init__(self, video_path: str, region_file: str, runtime_config=None):
        Pipeline.__init__(
            self,
            "DatasetViewer",
            factory(GetVideoFrame, video_path),
            TestExit,
            runtime_config=runtime_config,
        )
