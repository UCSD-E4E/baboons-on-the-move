import importlib
from argparse import ArgumentParser
from typing import Dict

import yaml

from baboons_on_the_move.cli_plugins.cli_plugin import CliPlugin


def main():
    parser = ArgumentParser(description="Baboon Command Line Interface")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    with open(
        "./baboons_on_the_move/cli_plugins/plugins.yaml", "r", encoding="utf8"
    ) as f:
        plugins_dict: Dict[str, Dict] = yaml.safe_load(f)

    # Plugins are loaded dynamically from ./baboons_on_the_move/cli_plugins/plugins.json
    for _, plugin in plugins_dict.items():
        for subcommand in plugin["subcommands"]:
            subparser = subparsers.add_parser(
                subcommand, description=plugin["description"]
            )

            module = importlib.import_module(
                "." + plugin["module"], "baboons_on_the_move.cli_plugins"
            )

            class_type = getattr(module, plugin["class"])

            cli_plugin: CliPlugin = class_type(subparser)
            subparser.set_defaults(run_plugin=cli_plugin.execute)

    args = parser.parse_args()
    args.run_plugin(args)


if __name__ == "__main__":
    main()
