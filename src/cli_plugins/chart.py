"""
Generates a chart representing the baboon tracking algorithm.
"""
from argparse import ArgumentParser, Namespace
from baboon_tracking import BaboonTracker
from baboon_tracking.csv_particle_filter_pipeline import CsvParticleFilterPipeline
from cli_plugins.cli_plugin import CliPlugin
from pipeline_viewer.viewer import PipelineViewer


class Chart(CliPlugin):
    """
    Generates a chart representing the baboon tracking algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        pipeline = BaboonTracker(args.pipeline_name)

        image = pipeline.flowchart_image()
        image.save("./output/flowchart.png")

        PipelineViewer(pipeline).run()
