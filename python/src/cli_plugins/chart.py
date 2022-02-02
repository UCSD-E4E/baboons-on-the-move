"""
Generates a chart representing the baboon tracking algorithm.
"""
from argparse import ArgumentParser, Namespace
from baboon_tracking import BaboonTracker
from baboon_tracking.preset_pipelines import preset_pipelines
from cli_plugins.cli_plugin import CliPlugin
from pipeline_viewer.viewer import PipelineViewer


class Chart(CliPlugin):
    """
    Generates a chart representing the baboon tracking algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-n",
            "--pipeline_name",
            type=str,
            choices=preset_pipelines.keys(),
            default="default",
            help="Preset pipeline to run",
        )

    def execute(self, args: Namespace):
        pipeline = BaboonTracker(args.pipeline_name)
        PipelineViewer(pipeline).run()
