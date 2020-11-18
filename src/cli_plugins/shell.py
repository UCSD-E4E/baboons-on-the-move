"""
Ensures that a venv is setup and that all necessary dependencies are installed.
Starts a shell in the venv once setup.
"""
from argparse import ArgumentParser, Namespace
import subprocess
from cli_plugins.cli_plugin import CliPlugin

from cli_plugins.install import install


class Shell(CliPlugin):
    """
    Ensures that a venv is setup and that all necessary dependencies are installed.
    Starts a shell in the venv once setup.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        install()

        subprocess.check_call(["poetry", "shell"])
