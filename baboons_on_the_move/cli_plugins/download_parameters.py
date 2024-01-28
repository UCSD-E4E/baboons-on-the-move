"""
CLI Plugin for downloading the best parameter from the cloud.
"""

from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin

from baboons_on_the_move.library.config import get_latest_config, save_config


class DownloadParameters(Plugin):
    """
    CLI Plugin for downloading the best parameter from the cloud.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

    def execute(self, args: Namespace):
        config, _, _ = get_latest_config()
        save_config(config)
