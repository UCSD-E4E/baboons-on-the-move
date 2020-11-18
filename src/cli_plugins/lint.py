"""
Lints all the Python files.
"""
from argparse import ArgumentParser
import subprocess
from pylint.lint import Run
from cli_plugins.cli_plugin import CliPlugin

from cli_plugins.utils import execute_node_script, get_python_files


class Lint(CliPlugin):
    """
    Lints all the Python files.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self):
        python_files = get_python_files()

        for f in python_files:
            subprocess.check_call(["black", "--check", f])

        Run(python_files)
        execute_node_script("pyright")
