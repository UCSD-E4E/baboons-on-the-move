"""
Plugin for calculating metrics.
"""
from argparse import ArgumentParser, Namespace

import pandas as pd

from cli_plugins.cli_plugin import CliPlugin
from library.metrics import get_metrics


class CalculateMetrics(CliPlugin):
    """
    Handles calculating metrics.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        """
        Calculate metrics for the specified video and output to Firebase.
        """

        data_frame = pd.DataFrame(get_metrics())
        data_frame.to_csv("input_metrics.csv")
