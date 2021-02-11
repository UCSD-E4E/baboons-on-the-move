from argparse import ArgumentParser, Namespace

import pandas as pd

from cli_plugins.cli_plugin import CliPlugin
from library.metrics import get_metrics


class CalculateMetrics(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        data_frame = pd.DataFrame(get_metrics())
        data_frame.to_csv("input_metrics.csv")
