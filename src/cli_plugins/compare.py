from argparse import ArgumentParser, Namespace
from sqlite3 import connect
from cli_plugins.cli_plugin import CliPlugin


class Compare(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-1",
            "--input1",
            help="The first input file.",
        )

        parser.add_argument(
            "-2",
            "--input2",
            help="The second input file.",
        )

    def execute(self, args: Namespace):
        input1 = args.input1
        input2 = args.input2

        with connect(input1) as db1:
            with connect(input2) as db2:
                cursor1 = db1.cursor()
                cursor2 = db2.cursor()

                found_regions1 = set(
                    cursor1.execute(
                        "SELECT x1, y1, x2, y2, frame FROM bayesian_filter_regions WHERE observed = 1"
                    )
                )
                found_regions2 = set(
                    cursor2.execute(
                        "SELECT x1, y1, x2, y2, frame FROM bayesian_filter_regions WHERE observed = 1"
                    )
                )

                missing1 = [r for r in found_regions1 if r not in found_regions2]
                missing1.sort(key=lambda x: x[-1])
                missing2 = [r for r in found_regions2 if r not in found_regions1]
                missing2.sort(key=lambda x: x[-1])

                print("Missing1")
                print(missing1)

                print("Missing2")
                print(missing2)
