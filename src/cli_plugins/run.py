"""
Starts the baboon tracker algorithm.
"""
from argparse import ArgumentParser, Namespace
import argparse
from baboon_tracking import BaboonTracker
from baboon_tracking.preset_pipelines import preset_pipelines
from cli_plugins.cli_plugin import CliPlugin  # pylint: disable=import-outside-toplevel


def str2bool(value):
    if isinstance(value, bool):
        return value
    elif value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolen value expected.")


class Run(CliPlugin):
    """
    Starts the baboon tracker algorithm.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-n",
            "--pipeline_name",
            type=str,
            choices=preset_pipelines.keys(),
            default="default",
            help="Preset pipeline to run",
        )

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

    def execute(self, args: Namespace):
        runtime_config = {"display": args.display, "save": args.save}

        BaboonTracker(args.pipeline_name, runtime_config=runtime_config).run()
