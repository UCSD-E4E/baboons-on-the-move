"""
Intializes classes, satisfying configuration and supplied parameters.
"""
import inspect
from typing import Callable, Dict
from config import get_config_part


def initializer(function: Callable, parameters_dict: Dict[str, any]):
    """
    Intializes classes, satisfying configuration and supplied parameters.
    """
    if hasattr(function, "config"):
        for key in function.config.keys():
            parameters_dict[key] = get_config_part(function.config[key])

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
