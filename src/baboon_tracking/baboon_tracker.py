"""
Provides an algorithm for extracting baboons from drone footage.
"""
from baboon_tracking.preset_pipelines import preset_pipelines, update_preset_pipelines
from pipeline.pipeline import Pipeline


class BaboonTracker(Pipeline):
    """
    An algorithm that attempts to extract baboons from drone footage.
    """

    def __init__(
        self, pipeline_name="default", input_file="input.mp4", runtime_config=None
    ):
        update_preset_pipelines(input_file=input_file, runtime_config=runtime_config)
        Pipeline.__init__(self, preset_pipelines[pipeline_name])

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self.stage.flowchart()
        return img
