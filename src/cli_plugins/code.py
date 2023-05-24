"""
Ensures that Visual Studio Code has the necessary Python extensions then launches VS Code.
"""
from argparse import ArgumentParser, Namespace
import json
import os
import subprocess
import sys
from typing import Dict
from colorama import Fore, Style

from cli_plugins.cli_plugin import CliPlugin


class Code(CliPlugin):
    """
    Ensures that Visual Studio Code has the necessary Python extensions then launches VS Code.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        self._ensure_vscode_settings()

        os.popen("code .")

    def _ensure_vscode_settings(self):
        with open(
            "./.vscode/settings.json.default", "r", encoding="utf8"
        ) as default_settings_file:
            default_settings: Dict = json.load(default_settings_file)

        if os.path.exists("./.vscode/settings.json"):
            with open("./.vscode/settings.json", "r", encoding="utf8") as settings_file:
                settings: Dict = json.load(settings_file)
        else:
            settings: Dict = {}

        for key, value in default_settings.items():
            settings[key] = value

        with open("./.vscode/settings.json", "w", encoding="utf8") as settings_file:
            json.dump(settings, settings_file, indent=4)
