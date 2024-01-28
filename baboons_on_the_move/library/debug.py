from typing import Callable


def trace(function: Callable):
    def trace_function(*args, **kwargs):
        print(f"Start {function.__name__}")

        results = function(*args, **kwargs)

        print(f"End {function.__name__}")

        return results

    return trace_function
