from typing import Callable


def config(parameter_name: str, key: str):
    def inner_function(function: Callable):
        if not hasattr(function, "config"):
            function.config = {}

        function.config[parameter_name] = key

        return function

    return inner_function


def last_stage(parameter: str):
    def inner_function(function: Callable):
        if not hasattr(function, "last_stage"):
            function.last_stage = []

        function.last_stage.append(parameter)

        return function

    return inner_function
