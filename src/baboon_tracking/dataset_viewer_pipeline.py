from baboon_tracking.decorators.debug import DisplayDebugRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.test_exit import TestExit
from baboon_tracking.stages.get_region_file_region import (
    # GetGroundTruthRegion,
    GetRegionFileRegion,
)
from pipeline.factory import factory
from pipeline.pipeline import Pipeline


class DatasetViewerPipeline(Pipeline):
    def __init__(self, video_path: str, runtime_config=None):
        Pipeline.__init__(
            self,
            "DatasetViewer",
            factory(GetVideoFrame, video_path),
            GetRegionFileRegion,
            # GetGroundTruthRegion,
            DisplayDebugRegions,
            TestExit,
            runtime_config=runtime_config,
        )
