"""
A schematic is for creating/modifying files on disk.
"""
from abc import abstractmethod
from argparse import ArgumentParser, Namespace


class Schematic:
    """
    A schematic is for creating/modifying files on disk.
    """

    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    @abstractmethod
    def execute(self, args: Namespace):
        """
        In a child class, this method is used for creating/modifying files.
        """
