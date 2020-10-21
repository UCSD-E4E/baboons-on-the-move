"""
This module is a CLI for helping with development of the Baboon Tracking Project.
"""

# These are default python packages.  No installed modules here.
import argparse
import importlib
import json
import os
import sys
from typing import Dict


def main():
    """
    Main entry point for CLI.
    """

    sys.path.append(os.getcwd() + "/src")

    parser = argparse.ArgumentParser(description="Baboon Command Line Interface")

    subparsers = parser.add_subparsers(dest='func')
    subparsers.required = True

    # We import the Cli plugin list from a json file instead of yaml,
    # Python's yaml support is not built in
    with open("./src/cli_plugins/plugins.json", "r") as f:
        plugins_dict = json.load(f)

    # Plugins are loaded dynamically from ./src/cli_plugins/plugins.json
    for plugin in plugins_dict["plugins"]:

        # We wait until the module is needed to import the module.
        # This allows the modules to not have to worry about if they are in a venv or not.
        def executor(plugin: Dict):
            # This creates a closure that allows us to use plugin.
            def internal():
                module = importlib.import_module(
                    "." + plugin["module"], "src.cli_plugins"
                )
                func = getattr(module, plugin["function"])

                func()

            return internal

        for subcommand in plugin["subcommands"]:
            subparser = subparsers.add_parser(subcommand, description=plugin['description'])
            subparser.set_defaults(func=executor(plugin))

    res = parser.parse_args()

    res.func()


if __name__ == "__main__":
    main()
