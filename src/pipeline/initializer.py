"""
Intializes classes, satisfying configuration and supplied parameters.
"""
import inspect
from typing import Callable, Dict
from config import get_config


def initializer(function: Callable, parameters_dict: Dict[str, any]):
    """
    Intializes classes, satisfying configuration and supplied parameters.
    """
    if hasattr(function, "config"):
        current_config: Dict[str, any] = get_config()

        for key in function.config.keys():
            key_parts = function.config[key].split("/")

            key_curr_config = current_config
            for key_part in key_parts:
                key_curr_config = key_curr_config[key_part]

            parameters_dict[key] = key_curr_config

    signature = inspect.signature(function.__init__)

    return function(
        *[
            _get_value_or_none(parameters_dict, k)
            for k in signature.parameters.keys()
            if k not in ("self", "args", "kwargs")
        ]
    )


def _get_value_or_none(parameters, key):
    if key in parameters:
        return parameters[key]

    return None
