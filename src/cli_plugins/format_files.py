"""
Formats all Python files.
"""
from argparse import ArgumentParser, Namespace
import subprocess
from cli_plugins.cli_plugin import CliPlugin

from cli_plugins.utils import get_python_files


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
