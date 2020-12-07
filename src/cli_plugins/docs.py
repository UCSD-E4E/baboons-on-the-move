"""
Generates sphinx documentation from source code
"""
from argparse import ArgumentParser, Namespace
import os
import subprocess

from cli_plugins.cli_plugin import CliPlugin


class Docs(CliPlugin):
    """
    Lints all the Python files.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        """
        Lints all the Python files.
        """
        subprocess.check_call(["make", "clean"], cwd="./docs/")

        packages = ["baboon_tracking", "pipeline", "scripts"]

        for package in packages:
            subprocess.check_call(
                [
                    "sphinx-apidoc",
                    "-o",
                    os.path.join("./docs/src/", package),
                    os.path.join("./src/", package),
                ]
            )

        subprocess.check_call(["make", "html"], cwd="./docs/")
