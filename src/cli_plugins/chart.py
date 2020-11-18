"""
Generates a chart representing the baboon tracking algorithm.
"""
from argparse import ArgumentParser
from baboon_tracking import BaboonTracker
from cli_plugins.cli_plugin import CliPlugin


class Chart(CliPlugin):
    """
    Generates a chart representing the baboon tracking algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self):
        BaboonTracker().flowchart().show()
