"""
A cli plugin that is used for creating Python files.
"""
import importlib
import json
from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin

from baboons_on_the_move.cli_plugins.schematics.schematic import Schematic


class Generate(Plugin):
    """
    A cli plugin that is used for creating Python files.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

        subparsers = parser.add_subparsers(dest="schematic")
        subparsers.required = True

        # We import the schematics list from a json file instead of yaml,
        # Python's yaml support is not built in
        with open(
            "./baboons_on_the_move/cli_plugins/schematics/schematics.json",
            "r",
            encoding="utf8",
        ) as f:
            schematics_dict = json.load(f)

        for schematic_dict in schematics_dict["schematics"]:
            subparser = subparsers.add_parser(
                schematic_dict["name"], description=schematic_dict["description"]
            )

            module = importlib.import_module(
                "." + schematic_dict["module"],
                "baboons_on_the_move.cli_plugins.schematics",
            )
            class_type = getattr(module, schematic_dict["class"])

            schematic: Schematic = class_type(subparser)
            subparser.set_defaults(schematic=schematic.execute)

    def execute(self, args: Namespace):
        args.schematic(args)
