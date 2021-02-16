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


def stage(parameter: str):
    """
    Satisfies a parameter with the last stage executed which is an instance of the mixin type.
    """

    def inner_function(function: Callable):
        if not hasattr(function, "stages"):
            function.stages = []

        function.stages.append(parameter)

        return function

    return inner_function
