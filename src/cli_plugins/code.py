"""
Ensures that Visual Studio Code has the necessary Python extensions then launches VS Code.
"""
from argparse import ArgumentParser, Namespace
import os
import subprocess
import sys
from colorama import Fore, Style

from cli_plugins.cli_plugin import CliPlugin


class Code(CliPlugin):
    """
    Ensures that Visual Studio Code has the necessary Python extensions then launches VS Code.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        self._ensure_vscode_plugin("eamodio.gitlens")
        self._ensure_vscode_plugin("ms-python.python")
        self._ensure_vscode_plugin("ms-python.vscode-pylance")
        self._ensure_vscode_plugin("VisualStudioExptTeam.vscodeintellicode")

        os.popen("code .")

    def _check_vscode_plugin(self, plugin: str):
        with os.popen("code --list-extensions") as f:
            installed = any([l.strip() == plugin for l in f.readlines()])

        return installed

    def _ensure_vscode_plugin(self, plugin: str):
        if not self._check_vscode_plugin(plugin):
            try:
                subprocess.check_call(
                    ["code", "--install-extension", plugin],
                    shell=(sys.platform == "win32"),
                )
            except subprocess.CalledProcessError as exception:
                print(
                    Fore.RED,
                    "WARNING: PLUGIN ",
                    plugin,
                    " NOT INSTALLED: ",
                    str(exception),
                    Style.RESET_ALL,
                )
