"""
This module is a CLI for helping with development of the Baboon Tracking Project.
"""

# These are default python packages.  No installed modules here.
import argparse
import importlib
import json
import os
import subprocess
import sys

from cli_plugins.cli_plugin import CliPlugin


def main():
    """
    Main entry point for CLI.
    """

    sys.path.append(os.getcwd() + "/src")

    if not os.getenv("VIRTUAL_ENV"):
        from src.cli_plugins.install import (  # pylint: disable=import-outside-toplevel
            install,
        )

        install()

        if len(sys.argv) > 1 and sys.argv[1].lower() not in ["shell", "install"]:
            subprocess.check_call(
                ["poetry", "run", "python", "./cli.py"] + sys.argv[1:],
                shell=(sys.platform == "win32"),
            )

            return

    parser = argparse.ArgumentParser(description="Baboon Command Line Interface")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # We import the Cli plugin list from a json file instead of yaml,
    # Python's yaml support is not built in
    with open("./src/cli_plugins/plugins.json", "r") as f:
        plugins_dict = json.load(f)

    # Plugins are loaded dynamically from ./src/cli_plugins/plugins.json
    for plugin in plugins_dict["plugins"]:
        for subcommand in plugin["subcommands"]:
            subparser = subparsers.add_parser(
                subcommand, description=plugin["description"]
            )

            module = importlib.import_module("." + plugin["module"], "src.cli_plugins")
            class_type = getattr(module, plugin["class"])

            cli_plugin: CliPlugin = class_type(subparser)
            subparser.set_defaults(command=cli_plugin.execute)

    res = parser.parse_args()

    res.command(res)


if __name__ == "__main__":
    main()
