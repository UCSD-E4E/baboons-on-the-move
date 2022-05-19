"""
Starts the baboon tracker algorithm.
"""
from argparse import ArgumentParser, Namespace
import argparse
from baboon_tracking import BaboonTracker
from baboon_tracking.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline
from cli_plugins.cli_plugin import CliPlugin  # pylint: disable=import-outside-toplevel


def str2bool(value):
    """
    Sets up a command line argument that can be converted to bool.
    """
    if isinstance(value, bool):
        return value
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if value.lower() in ("no", "false", "f", "n", "0"):
        return False

    raise argparse.ArgumentTypeError("Boolen value expected.")


class Run(CliPlugin):
    """
    Starts the baboon tracker algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-d",
            "--display",
            type=str2bool,
            default="yes",
            help="Indicates if should display images.",
        )

        parser.add_argument(
            "-s",
            "--save",
            type=str2bool,
            default="yes",
            help="Indicates if should save results.",
        )

        parser.add_argument(
            "-i",
            "--input",
            default="./data/input.mp4",
            help="Provides the input file for algorithm.",
        )

    def execute(self, args: Namespace):
        runtime_config = {"display": args.display, "save": args.save}

        # SqliteParticleFilterPipeline(args.input, runtime_config).run()
        BaboonTracker(args.input, runtime_config=runtime_config).run()
