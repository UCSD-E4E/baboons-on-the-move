"""
Reusable decorators for the pipeline.
"""
from typing import Callable


def config(parameter_name: str, key: str):
    """
    Satisfies a parameter with a value from config.yml
    """

    def inner_function(function: Callable):
        if not hasattr(function, "config"):
            function.config = {}

        function.config[parameter_name] = key

        return function

    return inner_function


def last_stage(parameter: str):
    """
    Satisfies a parameter with the last stage executed of the pipeline.
    """

    def inner_function(function: Callable):
        if not hasattr(function, "last_stage"):
            function.last_stage = []

        function.last_stage.append(parameter)

        return function

    return inner_function


def stage(parameter: str, is_property=False):
    """
    Satisfies a parameter with the last stage executed which is an instance of the mixin type.
    """

    def inner_function(function: Callable):
        if not hasattr(function, "stages"):
            function.stages = []

        function.stages.append((parameter, is_property))

        return function

    return inner_function


def stage_from_previous_iteration(parameter: str, is_property=True):
    """
    Satisfies a parameter with the last stage executed which is an instance of the mixin type from the previous execution.
    """

    if not is_property:
        raise Exception("This operation does not support constructor injection.")

    def inner_function(function: Callable):
        if not hasattr(function, "stages_from_prev_iter"):
            function.stages_from_prev_iter = []

        function.stages_from_prev_iter.append((parameter, is_property))

        return function

    return inner_function


def runtime_config(parameter: str, is_property=False):
    """
    Satisfies a parameter with the runtime configuration
    """

    def inner_function(function: Callable):
        if not hasattr(function, "runtime_configuration"):
            function.runtime_configuration = []

        function.runtime_configuration.append((parameter, is_property))

        return function

    return inner_function
