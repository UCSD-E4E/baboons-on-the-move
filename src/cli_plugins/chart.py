"""
Generates a chart representing the baboon tracking algorithm.
"""
from argparse import ArgumentParser, Namespace
from baboon_tracking import BaboonTracker
from cli_plugins.cli_plugin import CliPlugin


class Chart(CliPlugin):
    """
    Generates a chart representing the baboon tracking algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        BaboonTracker().flowchart().show()
