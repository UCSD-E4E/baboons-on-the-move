from baboon_tracking.stages.draw_regions import DrawRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.get_csv_baboon import GetCsvBaboon
from baboon_tracking.stages.particle_filter import ParticleFilterStage as ParticleFilter
from baboon_tracking.stages.test_exit import TestExit
from baboon_tracking.stages.display_progress import DisplayProgress
from pipeline.pipeline import Pipeline
from pipeline.factory import factory


class CsvParticleFilterPipeline(Pipeline):
    def __init__(self, runtime_config=None):
        Pipeline.__init__(
            self,
            "CsvParticleFilterPipeline",
            factory(GetVideoFrame, "./data/input.mp4"),
            GetCsvBaboon,
            ParticleFilter,
            DrawRegions,
            TestExit,
            DisplayProgress,
            runtime_config=runtime_config,
        )

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self.stage.flowchart()
        return img
