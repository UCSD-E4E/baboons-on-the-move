"""
Starts the baboon tracker algorithm.
"""
from argparse import ArgumentParser, Namespace
from baboon_tracking import BaboonTracker
from baboon_tracking.preset_pipelines import preset_pipelines
from cli_plugins.cli_plugin import CliPlugin  # pylint: disable=import-outside-toplevel


class Run(CliPlugin):
    """
    Starts the baboon tracker algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-n",
            "--pipeline_name",
            type=str,
            choices=preset_pipelines.keys(),
            help="Preset pipeline to run",
        )

    def execute(self, args: Namespace):
        BaboonTracker().run()
