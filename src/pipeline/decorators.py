from typing import Callable


def config(parameter_name: str, key: str):
    def inner_function(function: Callable):
        if not hasattr(function, "config"):
            function.config = {}

        function.config[parameter_name] = key

        return function

    return inner_function
