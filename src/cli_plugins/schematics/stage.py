"""
Implementation of a schematic that creates a custom stage in the specified location.
"""

import os
from argparse import ArgumentParser, Namespace
from cli_plugins.schematics.schematic import Schematic
from cli_plugins.schematics.string_builder import StringBuilder


class Stage(Schematic):
    """
    Implementation of a schematic that creates a custom stage in the specified location.
    """

    def __init__(self, parser: ArgumentParser):
        Schematic.__init__(self, parser)

        parser.add_argument("path")

    def execute(self, args: Namespace):
        path: str = os.path.realpath("./src/baboon_tracking/stages/%s" % args.path)

        if not path.endswith(".py"):
            path = "%s.py" % path

        class_name = "".join(
            [
                "%s%s" % (p[0].upper(), p[1:])
                for p in os.path.basename(path).replace(".py", "").split("_")
            ]
        )

        string_builder = StringBuilder()

        string_builder.append_line("from pipeline import Stage")
        string_builder.append_line("from pipeline.stage_result import StageResult")
        string_builder.append_line("")
        string_builder.append_line("")

        string_builder.append("class ")
        string_builder.append(class_name)
        string_builder.append_line("(Stage):")

        string_builder.append_line("    def __init__(self) -> None:")
        string_builder.append_line("        Stage.__init__(self)")
        string_builder.append_line("")

        string_builder.append_line("    def execute(self) -> StageResult:")
        string_builder.append_line("        return StageResult(True, True)")
        string_builder.append_line("")

        with open(path, "w") as f:
            f.write(string_builder.__str__())
