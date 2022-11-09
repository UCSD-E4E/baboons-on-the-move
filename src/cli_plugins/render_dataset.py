from argparse import ArgumentParser, Namespace
from posixpath import splitext
from baboon_tracking.dataset_viewer_pipeline import DatasetViewerPipeline

from cli_plugins.cli_plugin import CliPlugin
import cv2
from os.path import dirname, basename
from os import makedirs
from glob import glob
from library.args import ArgsParser, ArgumentParserBuilder
from tqdm import tqdm


class RenderDataset(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)
        ArgumentParserBuilder(parser).add_dataset().add_region_file()

    def execute(self, args: Namespace):
        parsed = ArgsParser(args)

        runtime_config = {
            "display": True,
            "save": True,
            "timings": False,
            "progress": True,
            "region_file": parsed.region_file,
        }

        DatasetViewerPipeline(
            f"{parsed.dataset_path}/img",
            runtime_config=runtime_config,
        ).run()
