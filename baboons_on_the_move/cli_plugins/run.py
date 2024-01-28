"""
Starts the baboon tracker algorithm.
"""
from argparse import ArgumentParser, Namespace

import numpy as np
import yaml
from bom_spot import MotionTrackerPipeline
from bom_spot.sqlite_particle_filter_pipeline import SqliteParticleFilterPipeline

from baboons_on_the_move.cli_plugins.cli_plugin import CliPlugin
from baboons_on_the_move.library.cli import str2bool, str2factory
from baboons_on_the_move.library.config import (
    get_config_declaration,
    get_config_options,
    set_config_part,
    set_config_path,
)
from baboons_on_the_move.library.dataset import (
    get_dataset_path,  # pylint: disable=import-outside-toplevel
)


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

    def _set_config(self, idx: int, X: np.ndarray, config_options):
        for i, (key, _, value_type) in enumerate(config_options):
            config_value = X[idx, i]
            if value_type == "int32":
                config_value = int(config_value)

            set_config_part(key, config_value)

    def execute(self, args: Namespace):
        if args.config.isnumeric():
            idx = int(args.config)

            with open("./config_declaration.yml", "r", encoding="utf8") as f:
                config_declaration = get_config_declaration("", yaml.safe_load(f))

            config_options = [
                (k, get_config_options(i), i["type"])
                for k, i in config_declaration.items()
                if "skip_learn" not in i or not i["skip_learn"]
            ]
            X = np.array(np.meshgrid(*[c for _, c, _ in config_options])).T.reshape(
                -1, len(config_options)
            )

            self._set_config(idx, X, config_options)
        else:
            set_config_path(args.config)

        if args.input.startswith("d:"):
            args.input = f"{get_dataset_path(args.input[2:])}/img"

        args.pipeline(args).run()
