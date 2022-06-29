from argparse import ArgumentParser, Namespace
from posixpath import splitext

from cli_plugins.cli_plugin import CliPlugin
from library.dataset import get_dataset_path
import cv2
from os.path import dirname, basename
from os import makedirs
from glob import glob
import pandas as pd


class RenderDataset(CliPlugin):
    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-d",
            "--dataset",
            default="Baboons/NeilThomas/001",
            help="Provides the input dataset for optimization.",
        )

    def execute(self, args: Namespace):
        dataset_path = get_dataset_path(args.dataset)

        img_path = f"{dataset_path}/img"
        gt_path = f"{dataset_path}/gt/gt.txt"

        gt = pd.read_csv(gt_path).to_numpy()

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

            # 1,0,1252,1202,20,22
            frame_regions = gt[gt[:, 0] == frame, 1:6]
            for identity, x1, y1, width, height in frame_regions:
                x2 = x1 + width
                y2 = y1 + width

                img = cv2.rectangle(
                    img,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

            # if id_str is not None:
            #     cv2.putText(
            #         debug_frame,
            #         id_str,
            #         (rect[0], rect[1] - 10),
            #         cv2.FONT_HERSHEY_SIMPLEX,
            #         0.5,
            #         color,
            #         2,
            #     )

            writer.write(img)

        writer.release()
