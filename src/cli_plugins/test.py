"""
Runs unit and integration tests
"""
from argparse import ArgumentParser, Namespace
import pytest

from cli_plugins.cli_plugin import CliPlugin


class Test(CliPlugin):
    """
    Run unit and integration tests
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        pytest.main()
