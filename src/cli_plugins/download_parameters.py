"""
CLI Plugin for downloading the best parameter from the cloud.
"""

from argparse import ArgumentParser, Namespace
from cli_plugins.cli_plugin import CliPlugin
from config import get_latest_config, save_config


class DownloadParameters(CliPlugin):
    """
    CLI Plugin for downloading the best parameter from the cloud.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        config, _, _ = get_latest_config()
        save_config(config)
