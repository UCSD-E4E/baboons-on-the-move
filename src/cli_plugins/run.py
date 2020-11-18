"""
Starts the baboon tracker algorithm.
"""
from argparse import ArgumentParser
from baboon_tracking import BaboonTracker
from cli_plugins.cli_plugin import CliPlugin  # pylint: disable=import-outside-toplevel


class Run(CliPlugin):
    """
    Starts the baboon tracker algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self):
        BaboonTracker().run()
