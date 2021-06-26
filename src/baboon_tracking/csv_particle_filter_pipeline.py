from typing import Dict
from baboon_tracking.stages.draw_regions import DrawRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.get_csv_baboon import GetCsvBaboon
from baboon_tracking.stages.particle_filter.particle_filter import ParticleFilter
from baboon_tracking.stages.test_exit import TestExit
from pipeline.parent_stage import ParentStage
from pipeline.pipeline import Pipeline
from pipeline.serial import Serial
from pipeline.factory import factory


class CsvParticleFilterPipeline(Pipeline):
    def __init__(self, runtime_config: Dict[str, any]):
        ParentStage.static_stages = []

        Pipeline.__init__(
            self,
            Serial(
                "CsvParticleFilterPipeline",
                runtime_config,
                factory(GetVideoFrame, "./data/input.mp4"),
                GetCsvBaboon,
                ParticleFilter,
                DrawRegions,
                TestExit,
            ),
        )

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self.stage.flowchart()
        return img
