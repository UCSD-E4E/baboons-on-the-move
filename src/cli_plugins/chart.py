"""
Generates a chart representing the baboon tracking algorithm.
"""
from argparse import ArgumentParser, Namespace
from baboon_tracking import BaboonTracker
from baboon_tracking.csv_particle_filter_pipeline import CsvParticleFilterPipeline
from baboon_tracking.preset_pipelines import preset_pipelines
from cli_plugins.cli_plugin import CliPlugin


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
        CsvParticleFilterPipeline(None).flowchart().show()

        # BaboonTracker(args.pipeline_name).flowchart().show()
