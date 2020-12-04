"""
Base class for Serial and Parallel classes.  Implements common functionality between the two.
"""
import inspect
from typing import Callable, List

from pipeline.initializer import initializer
from pipeline.models.time import Time

from .stage import Stage


class ParentStage(Stage):
    """
    Base class for Serial and Parallel classes.  Implements common functionality between the two.
    """

    static_stages = []

    def __init__(self, name: str, *stage_types: List[Callable]):
        Stage.__init__(self)

        self.name = name
        self.stages: List[Stage] = []
        for stage_type in stage_types:
            parameters_dict = {}

            if hasattr(stage_type, "last_stage"):
                for parameter in stage_type.last_stage:
                    parameters_dict[parameter] = self.stages[-1]

            if hasattr(stage_type, "stages"):
                for stage in stage_type.stages:
                    signature = inspect.signature(stage_type)
                    depen_type = signature.parameters[stage].annotation

                    most_recent_mixin = [
                        s
                        for s in reversed(self.static_stages)
                        if isinstance(s, depen_type)
                    ][0]

                    parameters_dict[stage] = most_recent_mixin

            self.stages.append(initializer(stage_type, parameters_dict=parameters_dict))
            self.static_stages.append(self.stages[-1])

    def get_time(self) -> Time:
        """
        Calculates the average time per execution of this stage.
        """

        time = Stage.get_time(self)
        time.children = [s.get_time() for s in self.stages]

        return time

    def on_destroy(self) -> None:
        for stage in self.stages:
            stage.on_destroy()
