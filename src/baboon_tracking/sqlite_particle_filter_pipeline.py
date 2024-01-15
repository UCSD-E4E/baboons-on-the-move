"""
Provides a pipeline that takes regions in a Sqlite database and uses the particle filter.
"""
from baboon_tracking.decorators.debug import DisplayDebugRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.get_sqlite_baboon import GetSqliteBaboon
from baboon_tracking.stages.particle_filter import ParticleFilterStage as ParticleFilter
from baboon_tracking.stages.save_computed_regions import SaveComputedRegions
from baboon_tracking.stages.save_hysteresis_regions import SaveHysteresisRegions
from baboon_tracking.stages.test_exit import TestExit
from bom_pipeline.pipeline import Pipeline
from bom_pipeline.factory import factory


class SqliteParticleFilterPipeline(Pipeline):
    """
    Provides a pipeline that takes regions in a Sqlite database and uses the particle filter.
    """

    def __init__(self, video_path: str, runtime_config=None):
        Pipeline.__init__(
            self,
            "SqliteParticleFilterPipeline",
            factory(GetVideoFrame, video_path),
            GetSqliteBaboon,
            ParticleFilter,
            SaveComputedRegions,
            SaveHysteresisRegions,
            DisplayDebugRegions,
            TestExit,
            runtime_config=runtime_config,
        )
