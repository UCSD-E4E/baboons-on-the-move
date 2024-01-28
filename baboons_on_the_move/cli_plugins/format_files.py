"""
Formats all Python files.
"""
import subprocess
from argparse import ArgumentParser, Namespace

from baboons_on_the_move.cli_plugins.cli_plugin import CliPlugin
from baboons_on_the_move.cli_plugins.utils import get_python_files


class FormatFiles(CliPlugin):
    """
    Formats all Python files.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        python_files = get_python_files()

        for python_file in python_files:
            subprocess.check_call(["black", python_file])
