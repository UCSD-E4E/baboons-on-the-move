"""
Starts the baboon tracker algorithm.
"""
from argparse import ArgumentParser, Namespace
import argparse
from typing import Callable, List
from baboon_tracking import BaboonTracker
from baboon_tracking.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline
from cli_plugins.cli_plugin import CliPlugin
from library.config import set_config_path
from library.dataset import get_dataset_path  # pylint: disable=import-outside-toplevel


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


def str2factory(*factories: List[Callable]):
    """
    Sets up a command line argument that can be converted to a stage factory.
    """

    def get_name(factory: Callable):
        name_parts = factory.__name__.split("_")
        return "".join([n.capitalize() for n in name_parts if n != "factory"])

    def internal(value: str):
        factory_names = {get_name(f): f for f in factories}

        if value in factory_names:
            return factory_names[value]

        raise argparse.ArgumentTypeError(
            f"{', '.join(factory_names)} value expected, recieved '{value}' instead."
        )

    return internal


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


def baboon_tracker_factory(args: Namespace):
    """
    Handles creating a baboon tracker.
    """

    runtime_config = get_runtime_config(args)
    return BaboonTracker(args.input, runtime_config=runtime_config)


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

        parser.add_argument(
            "-p",
            "--pipeline",
            type=str2factory(baboon_tracker_factory, particle_filter_factory),
            default="BaboonTracker",
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
            args.input = get_dataset_path(args.input[2:])

        args.pipeline(args).run()
