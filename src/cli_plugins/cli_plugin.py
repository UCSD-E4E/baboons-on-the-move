from abc import abstractmethod
from argparse import ArgumentParser


class CliPlugin:
    def __init__(self, parser: ArgumentParser):
        pass

    @abstractmethod
    def execute(self):
        pass
