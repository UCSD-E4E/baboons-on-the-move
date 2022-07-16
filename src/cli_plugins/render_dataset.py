from argparse import ArgumentParser, Namespace
import hashlib
from posixpath import splitext

from cli_plugins.cli_plugin import CliPlugin
from library.dataset import (
    dataset_filter_results_exists,
    get_dataset_filter_results,
    get_dataset_path,
)
import cv2
from os.path import dirname, basename
from os import makedirs
from glob import glob
import pandas as pd

from library.region_file import region_factory


class RenderDataset(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-d",
            "--dataset",
            default="Baboons/NeilThomas/001",
            help="Provides the input dataset for optimization.",
        )

        parser.add_argument(
            "-f", "--file", default=None, help="Provide the region file to render"
        )

    def execute(self, args: Namespace):
        with open("./config_declaration.yml", "rb") as f:
            config_hash = hashlib.md5(f.read()).hexdigest()

        dataset_path = get_dataset_path(args.dataset)

        img_path = f"{dataset_path}/img"

        region_path: str = args.file or ""
        if not region_path:
            region_path = f"{dataset_path}/gt/gt.txt"
        elif region_path.startswith("f:"):
            region_path = region_path[2:]
            enable_tracking = region_path[:3] == "yes"
            region_path = region_path[4:] if enable_tracking else region_path[3:]
            enable_persist = region_path[:3] == "yes"
            region_path = region_path[4:] if enable_persist else region_path[3:]
            idx = int(region_path)

            if not dataset_filter_results_exists(
                args.dataset, enable_tracking, enable_persist, idx, config_hash
            ):
                raise Exception("No cached version of the specified filter results.")

            get_dataset_filter_results(
                args.dataset, enable_tracking, enable_persist, idx, config_hash
            )

            region_path = "./output/results.db"

        regions = region_factory(region_path)

        target_path = f"./output/{args.dataset}.mp4"
        target_dir = dirname(target_path)

        makedirs(target_dir, exist_ok=True)

        imgs = glob(f"{img_path}/*.jpg")
        imgs.sort(key=lambda x: x)

        img = cv2.imread(imgs[0])
        height, width, _ = img.shape

        writer = cv2.VideoWriter(
            target_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            30,
            (width, height),
        )

        for img_path in imgs:
            frame = int(splitext(basename(img_path))[0])
            img = cv2.imread(img_path)

            for region in regions.frame_regions(frame):
                x1, y1, x2, y2 = region.rectangle
                id_str = region.id_str

                img = cv2.rectangle(
                    img,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

                if id_str is not None:
                    cv2.putText(
                        img,
                        id_str,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

            writer.write(img)

        writer.release()
