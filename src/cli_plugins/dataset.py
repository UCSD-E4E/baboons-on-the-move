"""
CLI Plugin for creating a dataset from a video and ground truth xml.
"""

import subprocess
from argparse import ArgumentParser, Namespace
from glob import glob
from os import makedirs, unlink, rename
from os.path import splitext, basename, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

from baboon_tracking.models.region import Region
from cli_plugins.cli_plugin import CliPlugin
from library.cli import str2bool
from library.region_file import region_factory


class Dataset(CliPlugin):
    """
    CLI Plugin for creating a dataset from a video and ground truth xml.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        parser.add_argument(
            "-v",
            "--video",
            default="./data/input.mp4",
            help="Provides the input video for creating a dataset.",
        )

        parser.add_argument(
            "-x",
            "--xml",
            default="./data/input.xml",
            help="Provides the input xml for creating a dataset.",
        )

        parser.add_argument(
            "-n",
            "--name",
            default="Baboons/NeilThomas/001",
            help="Provides the name for creating the dataset.",
        )

        parser.add_argument(
            "-s",
            "--start",
            default=90,
            help="Provides the start frame for the dataset.",
        )

        parser.add_argument(
            "-e", "--end", default=419, help="Provides the end frame for the dataset."
        )

        parser.add_argument(
            "-m",
            "--enable-motion-only",
            default="yes",
            type=str2bool,
            help="Enable motion only in resultant gt.txt.",
        )

    def _generate_img(self, video: str, start: int, end: int, dataset_path: str):
        img_path = f"{dataset_path}/img"
        makedirs(img_path, exist_ok=True)

        # ffmpeg -i input.mp4 %06d.jpg
        subprocess.check_call(["ffmpeg", "-i", video, f"{img_path}/%06d.jpg"])

        files = glob(f"{img_path}/**.jpg")
        files.sort(key=lambda x: x)

        frame_shift = start - 1 if start else 0
        for file in files:
            parent_dir = dirname(file)
            file_name = basename(file)
            frame_number, _ = splitext(file_name)
            frame_number = int(frame_number)

            if (start and frame_number < start) or (end and frame_number > end):
                unlink(file)
                continue

            frame_number -= frame_shift
            rename(file, f"{parent_dir}/{frame_number:0>6}.jpg")

    def _get_ground_truth(self, xml: str):
        region_file = region_factory(xml)
        data = region_file.to_numpy()
        data[:, 4:6] -= data[:, 2:4]

        return data

    def _is_motion(
        self,
        frame: int,
        identity: int,
        data: np.ndarray,
        hysteresis=(5, 5),
    ):
        data = data.astype(float)

        selector = np.logical_and(data[:, 0] == frame, data[:, 1] == identity)
        idx = np.argmax(selector)

        for j, h in enumerate(hysteresis):
            direction = j * 2 - 1

            for i in range(h):
                k = i + 1

                # Can we find it in the previous frame
                previous_selector = np.logical_and(
                    data[:, 0] == frame + direction * k,
                    data[:, 1] == identity,
                )
                if not np.any(previous_selector):
                    # We didn't see this item last frame
                    continue
                previous_idx = np.argmax(previous_selector)

                region = Region(
                    (
                        data[idx, 2],
                        data[idx, 3],
                        data[idx, 2] + data[idx, 4],
                        data[idx, 3] + data[idx, 5],
                    )
                )

                previous_region = Region(
                    (
                        data[previous_idx, 2],
                        data[previous_idx, 3],
                        data[previous_idx, 2] + data[previous_idx, 4],
                        data[previous_idx, 3] + data[previous_idx, 5],
                    )
                )

                iou = region.iou(previous_region)
                if iou <= 0.425:
                    return True

        return False

    def _generate_gt(
        self, xml: str, start: int, end: int, motion_only: bool, dataset_path: str
    ):
        start = start or 0

        gt_path = f"{dataset_path}/gt"
        makedirs(gt_path, exist_ok=True)

        data = self._get_ground_truth(xml)

        if end:
            data = data[data[:, 0] <= end, :]

        frame_shift = start - 1 if start else 0
        data = data[data[:, 0] >= start]
        data[:, 0] -= frame_shift

        if motion_only:
            unique_frames = set(data[:, 0])
            unique_identities = set(data[:, 1])

            # data = pd.read_csv(
            #     "./data/Datasets/Baboons/NeilThomas/001/gt/gt.txt"
            # ).to_numpy()

            for frame in tqdm(unique_frames):
                for identity in unique_identities:
                    selector = np.logical_and(
                        data[:, 0] == frame, data[:, 1] == identity
                    )

                    if not np.any(selector):
                        continue

                    idx = np.argmax(selector)
                    if not self._is_motion(frame, identity, data, hysteresis=[20, 30]):
                        data = np.delete(data, idx, axis=0)

            # for identity in tqdm(unique_identities):
            #     frames = data[data[:, 1] == identity, 0]

            #     prev_frame = None
            #     for frame in frames:
            #         if not prev_frame:
            #             prev_frame = frame
            #             continue

            #         gap = frame - prev_frame
            #         if gap <= 6:
            #             for g in range(2, gap + 1):
            #                 missing_frame = prev_frame + g - 1
            #                 original_selector = np.logical_and(
            #                     original[:, 0] == missing_frame,
            #                     original[:, 1] == identity,
            #                 )
            #                 data_selector = np.logical_and(
            #                     data[:, 0] == frame, data[:, 1] == identity
            #                 )

            #                 original_idx = np.argmax(original_selector)
            #                 data_idx = np.argmax(data_selector)

            #                 data = np.insert(
            #                     data, data_idx, original[original_idx, :], axis=0
            #                 )

            #         prev_frame = frame

            # for identity in tqdm(unique_identities):
            #     frames = data[data[:, 1] == identity, 0]

            #     contig = 0
            #     prev_frame = None
            #     for frame in frames:
            #         if not prev_frame:
            #             prev_frame = frame
            #             continue

            #         gap = frame - prev_frame
            #         if gap == 1:
            #             contig += 1
            #         else:
            #             if contig <= 15:
            #                 selector = np.logical_and(
            #                     data[:, 0] == prev_frame, data[:, 1] == identity
            #                 )
            #                 idx = np.argmax(selector)
            #                 data = np.delete(data, idx, axis=0)

            #             contig = 0

            #         prev_frame = frame

        height, _ = data.shape

        df = pd.DataFrame()

        df["Frame"] = data[:, 0]
        df["Identity"] = data[:, 1]
        df["x1"] = data[:, 2]
        df["y1"] = data[:, 3]
        df["width"] = data[:, 4]
        df["height"] = data[:, 5]
        df["1"] = np.ones(height, dtype=int)
        df["2"] = -1 * np.ones(height, dtype=int)
        df["3"] = -1 * np.ones(height, dtype=int)
        df["4"] = -1 * np.ones(height, dtype=int)

        df.to_csv(f"{gt_path}/gt.txt", index=False, header=False)

    def execute(self, args: Namespace):
        dataset_path = f"./data/Datasets/{args.name}"

        # self._generate_img(args.video, args.start, args.end, dataset_path)
        self._generate_gt(
            args.xml, args.start, args.end, args.enable_motion_only, dataset_path
        )
