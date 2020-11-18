"""
A cli plugin that is used for creating Python files.
"""
from argparse import ArgumentParser, Namespace
import importlib
import json
from cli_plugins.cli_plugin import CliPlugin
from cli_plugins.schematics.schematic import Schematic


class Generate(CliPlugin):
    """
    A cli plugin that is used for creating Python files.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        subparsers = parser.add_subparsers(dest="schematic")
        subparsers.required = True

        # We import the schematics list from a json file instead of yaml,
        # Python's yaml support is not built in
        with open("./src/cli_plugins/schematics/schematics.json", "r") as f:
            schematics_dict = json.load(f)

        for schematic_dict in schematics_dict["schematics"]:
            subparser = subparsers.add_parser(
                schematic_dict["name"], description=schematic_dict["description"]
            )

            module = importlib.import_module(
                "." + schematic_dict["module"], "src.cli_plugins.schematics"
            )
            class_type = getattr(module, schematic_dict["class"])

            schematic: Schematic = class_type(subparser)
            subparser.set_defaults(schematic=schematic.execute)

    def execute(self, args: Namespace):
        args.schematic(args)
