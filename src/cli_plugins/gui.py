from argparse import ArgumentParser, Namespace
from cli_plugins.cli_plugin import CliPlugin
from gui.app import App


class Gui(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        self.app = App()

    def execute(self, args: Namespace):
        self.app.start()
