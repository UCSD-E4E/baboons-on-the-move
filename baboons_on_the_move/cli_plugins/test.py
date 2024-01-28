"""
Runs unit and integration tests
"""
import sys
from argparse import ArgumentParser, Namespace

import pytest
from bom_common.pluggable_cli import Plugin


class Test(Plugin):
    """
    Run unit and integration tests
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

    def execute(self, args: Namespace):
        exit_code = pytest.main(["-s"])
        sys.exit(exit_code)
