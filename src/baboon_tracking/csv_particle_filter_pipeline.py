from typing import Dict
from baboon_tracking.stages.draw_regions import DrawRegions
from baboon_tracking.stages.get_video_frame import GetVideoFrame
from baboon_tracking.stages.get_csv_baboon import GetCsvBaboon
from baboon_tracking.stages.test_exit import TestExit
from pipeline.pipeline import Pipeline
from pipeline.serial import Serial
from pipeline.factory import factory


class CsvParticleFilterPipeline(Pipeline):
    def __init__(self, runtime_config: Dict[str, any]):
        Pipeline.__init__(
            self,
            Serial(
                "CsvParticleFilterPipeline",
                runtime_config,
                factory(GetVideoFrame, "./data/input.mp4"),
                GetCsvBaboon,
                DrawRegions,
                TestExit,
            ),
        )
