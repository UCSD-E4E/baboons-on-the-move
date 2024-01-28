"""
Formats all Python files.
"""
import subprocess
from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin

from baboons_on_the_move.cli_plugins.utils import get_python_files


class FormatFiles(Plugin):
    """
    Formats all Python files.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

    def execute(self, args: Namespace):
        python_files = get_python_files()

        for python_file in python_files:
            subprocess.check_call(["black", python_file])
