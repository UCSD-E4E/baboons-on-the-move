"""
Plugin for calculating metrics.
"""
from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin

from baboons_on_the_move.library.args import ArgsParser, ArgumentParserBuilder

from ..library.metrics import Metrics


class CalculateMetrics(Plugin):
    """
    Handles calculating metrics.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)
        ArgumentParserBuilder(
            parser
        ).add_dataset().add_region_file().add_ground_truth_file().add_max_size().add_allow_overlap()

    def execute(self, args: Namespace):
        """
        Calculate metrics for the specified video and output to Firebase.
        """
        parsed = ArgsParser(args)

        metrics = Metrics(
            parsed.regions,
            parsed.ground_truth_regions,
            max_width=parsed.max_width,
            max_height=parsed.max_height,
            allow_overlap=parsed.allow_overlap,
        )
        recall, precision, f1, df = metrics.calculate_metrics()

        df.to_csv("./output/metrics.csv")

        print((recall, precision, f1))
