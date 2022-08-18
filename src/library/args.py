from argparse import ArgumentParser
import hashlib

from library.dataset import (
    dataset_filter_results_exists,
    get_dataset_filter_results,
    get_dataset_path,
)
from library.region_file import region_factory


class ArgumentParserBuilder:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def add_dataset(self):
        self.parser.add_argument(
            "-d",
            "--dataset",
            default="Baboons/NeilThomas/001",
            help="Provides the input dataset for optimization.",
        )

        return self

    def add_region_file(self):
        self.parser.add_argument(
            "-f",
            "--region_file",
            default=None,
            help="Provide the region file to process",
        )

        return self

    def add_ground_truth_file(self):
        self.parser.add_argument(
            "-g",
            "--ground_truth",
            default=None,
            help="Provide the ground truth file to process",
        )

        return self


class ArgsParser:
    def __init__(self, args):
        has_dataset = False
        with open("./config_declaration.yml", "rb") as f:
            self.config_hash = hashlib.md5(f.read()).hexdigest()

        if hasattr(args, "dataset"):
            self.dataset: str = args.dataset
            self.dataset_path = get_dataset_path(self.dataset)
            has_dataset = True

        if hasattr(args, "region_file"):
            self.region_file = args.region_file or ""
            if not self.region_file and has_dataset:
                self.region_file = f"{self.dataset_path}/gt/gt.txt"
            elif self.region_file.startswith("f:") and has_dataset:
                self.region_file = self.region_file[2:]
                enable_tracking = self.region_file[:3] == "yes"
                self.region_file = (
                    self.region_file[4:] if enable_tracking else self.region_file[3:]
                )
                enable_persist = self.region_file[:3] == "yes"
                self.region_file = (
                    self.region_file[4:] if enable_persist else self.region_file[3:]
                )
                idx = int(self.region_file)

                if not dataset_filter_results_exists(
                    self.dataset, enable_tracking, enable_persist, idx, self.config_hash
                ):
                    raise Exception(
                        "No cached version of the specified filter results."
                    )

                get_dataset_filter_results(
                    self.dataset, enable_tracking, enable_persist, idx, self.config_hash
                )

                self.region_file = "./output/results.db"

            if self.region_file:
                self.regions = region_factory(self.region_file)

        if hasattr(args, "ground_truth"):
            self.ground_truth = args.ground_truth or ""
            if not self.ground_truth and has_dataset:
                self.ground_truth = f"{self.dataset_path}/gt/gt.txt"

            if self.ground_truth:
                self.ground_truth_regions = region_factory(self.ground_truth)
