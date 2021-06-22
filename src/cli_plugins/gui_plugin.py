from argparse import ArgumentParser, Namespace
from sys import exit
from cli_plugins.cli_plugin import CliPlugin
from gui.app import BaboonTrackingApp


class Gui(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        self.app = BaboonTrackingApp()

    def execute(self, args: Namespace):
        self.app.run()
