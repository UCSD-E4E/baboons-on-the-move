"""
Contains objects for representing slices of time.
"""
from typing import Iterable


class Time:
    """
    An object that represents a slice of execution time.
    """

    def __init__(
        self, name: str, execution_time: float, children: Iterable["Time"] = None
    ):
        self.name = name
        self.execution_time = execution_time
        self.children = children

    def print_to_console(self, indentation=1):
        """
        Prints the current time object and its children to the console.
        """

        print(
            "{indentation}{name}: {execution_time} ms".format(
                indentation=("  " * indentation),
                name=self.name,
                execution_time=round(self.execution_time * 1000, 2),
            )
        )

        if self.children:
            for child in self.children:
                child.print_to_console(indentation + 1)
