"""
Lints all the Python files.
"""
import subprocess
from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin
from pylint.lint import Run

from baboons_on_the_move.cli_plugins.utils import execute_node_script, get_python_files


class Lint(Plugin):
    """
    Lints all the Python files.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

    def execute(self, args: Namespace):
        python_files = get_python_files()

        for f in python_files:
            subprocess.check_call(["black", "--check", f])

        Run(python_files)
        execute_node_script("pyright")
