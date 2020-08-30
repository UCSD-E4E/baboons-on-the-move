"""
This module is a CLI for helping with development of the Baboon Tracking Project.
"""

# These are default python packages.  No installed modules here.
import argparse
import importlib
import json


def main():
    """
    Main entry point for CLI.
    """

    parser = argparse.ArgumentParser(description="Baboon Command Line Interface")

    subparsers = parser.add_subparsers()

    # We import the Cli plugin list from a json file instead of yaml,
    # Python's yaml support is not built in
    with open("./src/cli_plugins/plugins.json", "r") as f:
        plugins_dict = json.load(f)

    for plugin in plugins_dict["plugins"]:
        module = importlib.import_module("." + plugin["module"], "src.cli_plugins")

        for subcommand in plugin["subcommands"]:
            subparser = subparsers.add_parser(subcommand)
            func = getattr(module, plugin["function"])
            subparser.set_defaults(func=func)

    res = parser.parse_args()

    res.func()


if __name__ == "__main__":
    main()
