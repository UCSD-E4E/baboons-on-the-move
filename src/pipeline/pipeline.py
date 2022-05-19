"""
Implements a base pipeline.
"""

from abc import ABC
import inspect
from typing import Callable, List
from tqdm import tqdm

from pipeline.parent_stage import ParentStage

from pipeline.stage import Stage
from pipeline.serial import Serial
from pipeline.parallel import Parallel
from pipeline.stage_result import StageResult

from library.caf import Caffine


class Pipeline(ABC):
    """
    Implements a base pipeline.
    """

    iterations = 0

    def __init__(
        self, name: str, *stage_types: List[Stage], parallel=False, runtime_config=None
    ):
        ParentStage.static_stages = []
        self._progressbar: tqdm = None

        if parallel:
            self.stage = Parallel(name, runtime_config, *stage_types)
        else:
            self.stage = Serial(name, runtime_config, *stage_types)

        for result in ParentStage.static_stages:
            function = type(result)

            if hasattr(function, "stages_from_prev_iter"):
                for stage, is_property in function.stages_from_prev_iter:
                    if not is_property:
                        continue

                    func = getattr(function, stage)

                    signature = inspect.signature(func)
                    depen_type = [
                        signature.parameters[p]
                        for i, p in enumerate(signature.parameters)
                        if i == 1
                    ][0].annotation

                    most_recent_mixin = [
                        s
                        for s in reversed(ParentStage.static_stages)
                        if isinstance(s, depen_type)
                    ][0]

                    func(result, most_recent_mixin)
        self.stage.on_init()

    def flowchart_image(self):
        """
        Generates a chart representing the algorithm.
        """

        (
            img,
            _,
            _,
        ) = self.stage.flowchart_image()
        return img

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
            self.progress()

            if not result.continue_pipeline:
                self._progressbar.close()

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

    def progress(self):
        """
        Increments the progress bar by 1.
        """

        if self._progressbar is None:
            self._progressbar = tqdm(total=int(Pipeline.iterations))

        self._progressbar.update(1)