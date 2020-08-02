from typing import Callable


def factory(function: Callable, *args: any, **kwargs):
    def wrapper():
        return function(*args, **kwargs)

    return wrapper
