from argparse import ArgumentParser, Namespace

from numpy.core.numeric import Inf
from cli_plugins.cli_plugin import CliPlugin
from library.metrics import calculate_loss, get_metrics
from config import get_latest_config, step_config, set_config, save_cloud_config


LOSS_THRESH = 0.01


class Optimize(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        prev_loss = Inf
        loss = -Inf

        while True:
            config, prev_loss, pulled_from_cloud = get_latest_config()
            if pulled_from_cloud:
                config = step_config(config)

            set_config(config)
            loss = calculate_loss(get_metrics())
            better = loss < prev_loss
            save_cloud_config(config, loss, better)

            should_stop = abs(prev_loss - loss) < LOSS_THRESH

            if better:
                prev_loss = loss

            if should_stop:
                break
