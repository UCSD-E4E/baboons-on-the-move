"""
Implements a base pipeline.
"""

from abc import ABC
from typing import Callable

from library.caf import Caffine
from pipeline.parent_stage import ParentStage
from pipeline.stage import Stage
from pipeline.stage_result import StageResult


class Pipeline(ABC):
    """
    Implements a base pipeline.
    """

    def __init__(self, stage: Stage):
        self.stage = stage
        self.stage.on_init()

    def step(self) -> StageResult:
        """
        Runs one step of the algorithm.
        """
        self.stage.before_execute()
        result = self.stage.execute()
        self.stage.after_execute()

        return result

    def run(self):
        """
        Runs the algorithm until it finishes.
        """

        caf = Caffine()
        request_id = caf.request()

        while True:
            result = self.step()

            if not result.continue_pipeline:
                print("Average Runtime per stage:")
                self.stage.get_time().print_to_console()

                self.stage.on_destroy()
                caf.release(request_id)

                return

    def get(self, stage_type: Callable):
        """
        Get a type from the pipeline.
        """
        candidate_stages = [
            s for s in ParentStage.static_stages if isinstance(s, stage_type)
        ]

        return candidate_stages[-1]
