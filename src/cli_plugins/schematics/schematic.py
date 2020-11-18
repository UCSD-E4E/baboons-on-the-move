from abc import abstractmethod
from argparse import ArgumentParser, Namespace


class Schematic:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    @abstractmethod
    def execute(self, args: Namespace):
        pass
