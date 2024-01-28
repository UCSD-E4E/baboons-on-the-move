"""
A CLI plugin to render a generated region file and a ground truth file
to a single video files based off of the supplied dataset.
"""

from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin

from baboons_on_the_move.library.args import ArgsParser, ArgumentParserBuilder

# from baboon_tracking.dataset_viewer_pipeline import DatasetViewerPipeline


class RenderDataset(Plugin):
    """
    A CLI plugin to render a generated region file and a ground truth file
    to a single video files based off of the supplied dataset.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

        ArgumentParserBuilder(
            parser
        ).add_dataset().add_region_file().add_ground_truth_file()

    def execute(self, args: Namespace):
        parsed = ArgsParser(args)

        runtime_config = {
            "display": True,
            "save": True,
            "timings": False,
            "progress": True,
            "region_file": parsed.region_file,
            "ground_truth": parsed.ground_truth,
        }

        DatasetViewerPipeline(
            f"{parsed.dataset_path}/img",
            runtime_config=runtime_config,
        ).run()
