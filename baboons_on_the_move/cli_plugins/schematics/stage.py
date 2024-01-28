"""
Implementation of a schematic that creates a custom stage in the specified location.
"""

import os
from argparse import ArgumentParser, Namespace

from baboons_on_the_move.cli_plugins.schematics.schematic import Schematic
from baboons_on_the_move.cli_plugins.schematics.string_builder import StringBuilder


class Stage(Schematic):
    """
    Implementation of a schematic that creates a custom stage in the specified location.
    """

    def __init__(self, parser: ArgumentParser):
        Schematic.__init__(self, parser)

        parser.add_argument("path")

    def execute(self, args: Namespace):
        path: str = os.path.realpath(f"./src/baboon_tracking/stages/{args.path}")

        if not path.endswith(".py"):
            path = f"{path}.py"

        class_name = "".join(
            [
                f"{p[0].upper()}{p[1:]}"
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

        with open(path, "w", encoding="utf8") as f:
            f.write(str(string_builder))

        os.popen(f"code {path}")
