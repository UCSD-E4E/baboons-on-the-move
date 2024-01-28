"""
Generates sphinx documentation from source code
"""
import os
import subprocess
from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin


class Docs(Plugin):
    """
    Lints all the Python files.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

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
