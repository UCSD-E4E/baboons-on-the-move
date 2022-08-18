"""
Plugin for calculating metrics.
"""
from argparse import ArgumentParser, Namespace
from cli_plugins.cli_plugin import CliPlugin
from library.args import ArgsParser, ArgumentParserBuilder
from ..library.metrics import Metrics


class CalculateMetrics(CliPlugin):
    """
    Handles calculating metrics.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)
        ArgumentParserBuilder(
            parser
        ).add_dataset().add_region_file().add_ground_truth_file()

    def execute(self, args: Namespace):
        """
        Calculate metrics for the specified video and output to Firebase.
        """
        parsed = ArgsParser(args)

        metrics = Metrics(parsed.regions, parsed.ground_truth_regions)
        recall, precision, f1 = metrics.calculate_metrics()

        print((recall, precision, f1))
