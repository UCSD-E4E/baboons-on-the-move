"""
Starts the baboon tracker algorithm.
"""
from argparse import ArgumentParser, Namespace
import argparse
from typing import Callable, List
from baboon_tracking import MotionTrackerPipeline
from baboon_tracking.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline
from cli_plugins.cli_plugin import CliPlugin
from library.config import set_config_path
from library.dataset import get_dataset_path  # pylint: disable=import-outside-toplevel
from library.cli import str2bool, str2factory


def get_runtime_config(args: Namespace):
    """
    Converts parsed arguments to a runtime config dictionary.
    """

    return {
        "display": args.display,
        "save": args.save,
        "timings": True,
        "progress": True,
    }


def particle_filter_factory(args: Namespace):
    """
    Handles creating a particle filter.
    """

    runtime_config = get_runtime_config(args)
    return SqliteParticleFilterPipeline(args.input, runtime_config=runtime_config)


def motion_tracker_factory(args: Namespace):
    """
    Handles creating a motion tracker.
    """

    runtime_config = get_runtime_config(args)
    return MotionTrackerPipeline(args.input, runtime_config=runtime_config)


class Run(CliPlugin):
    """
    Starts the motion tracker algorithm.
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

        parser.add_argument(
            "-p",
            "--pipeline",
            type=str2factory(motion_tracker_factory, particle_filter_factory),
            default="MotionTracker",
            help="Indicates which pipeline should be run.",
        )

        parser.add_argument(
            "-c",
            "--config",
            default="./config.yml",
            help="The configuration file used for this run.",
        )

    def execute(self, args: Namespace):
        set_config_path(args.config)

        if args.input.startswith("d:"):
            args.input = f"{get_dataset_path(args.input[2:])}/img"

        args.pipeline(args).run()
