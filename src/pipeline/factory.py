"""
Factory function used to wrap a function with zero parameters.
"""
from typing import Callable


def factory(function: Callable, *args: any, **kwargs):
    """
    Wraps a function, passing args and kwargs to it.  Returns a wrapper with 0 parameters.
    """

    def wrapper():
        return function(*args, **kwargs)

    return wrapper
