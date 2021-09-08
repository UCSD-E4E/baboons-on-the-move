"""
Runs unit and integration tests
"""
from argparse import ArgumentParser, Namespace
import sys
import pytest

from cli_plugins.cli_plugin import CliPlugin


class Test(CliPlugin):
    """
    Run unit and integration tests
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        exit_code = pytest.main(["-s"])
        sys.exit(exit_code)
