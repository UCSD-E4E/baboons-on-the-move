from baboon_tracking.decorators.debug import DisplayDebugRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.get_sqlite_baboon import GetSqliteBaboon
from baboon_tracking.stages.particle_filter import ParticleFilterStage as ParticleFilter
from baboon_tracking.stages.save_computed_regions import SaveComputedRegions
from baboon_tracking.stages.test_exit import TestExit
from pipeline.pipeline import Pipeline
from pipeline.factory import factory


class SqliteParticleFilterPipeline(Pipeline):
    def __init__(self, video_path: str, runtime_config=None):
        Pipeline.__init__(
            self,
            "SqliteParticleFilterPipeline",
            factory(GetVideoFrame, video_path),
            GetSqliteBaboon,
            ParticleFilter,
            SaveComputedRegions,
            DisplayDebugRegions,
            TestExit,
            runtime_config=runtime_config,
        )
