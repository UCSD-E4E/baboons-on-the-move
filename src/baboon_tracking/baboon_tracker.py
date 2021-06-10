"""
Provides an algorithm for extracting baboons from drone footage.
"""
from typing import Callable
from baboon_tracking.preset_pipelines import preset_pipelines, update_preset_pipelines
from pipeline.parent_stage import ParentStage
from pipeline.stage_result import StageResult


class BaboonTracker:
    """
    An algorithm that attempts to extract baboons from drone footage.
    """

    def __init__(
        self, pipeline_name="default", input_file="input.mp4", runtime_config=None
    ):
        update_preset_pipelines(input_file=input_file, runtime_config=runtime_config)
        self._pipeline = preset_pipelines[pipeline_name]

    def step(self) -> StageResult:
        """
        Runs one step of the algorithm.
        """
        self._pipeline.before_execute()
        result = self._pipeline.execute()
        self._pipeline.after_execute()

        return result

    def run(self):
        """
        Runs the algorithm until it finishes.
        """

        while True:
            result = self.step()

            if not result.continue_pipeline:
                print("Average Runtime per stage:")
                self._pipeline.get_time().print_to_console()

                self._pipeline.on_destroy()

                return

    def get(self, stage_type: Callable):
        """
        Get a type from the pipeline.
        """
        candidate_stages = [
            s for s in ParentStage.static_stages if isinstance(s, stage_type)
        ]

        return candidate_stages[-1]

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self._pipeline.flowchart()
        return img
