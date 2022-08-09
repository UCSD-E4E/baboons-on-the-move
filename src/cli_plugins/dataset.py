from argparse import ArgumentParser, Namespace
from os import makedirs, unlink, rename
import subprocess
from glob import glob
from os.path import splitext, basename, dirname
from library.labeled_data import get_regions_from_xml

from cli_plugins.cli_plugin import CliPlugin
from cli_plugins.optimize import str2bool
import numpy as np
import pandas as pd


class Dataset(CliPlugin):
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
        regions = get_regions_from_xml(xml)
        regions.sort(key=lambda x: x[0])

        frames, identities, xtls, ytls, xbrs, ybrs = zip(*regions)

        frames = np.array(frames)
        identities = np.array(identities)
        xtls = np.array(xtls)
        ytls = np.array(ytls)
        xbrs = np.array(xbrs)
        ybrs = np.array(ybrs)

        widths = xbrs - xtls
        heights = ybrs - ytls

        data = np.zeros((len(frames), 6), dtype=int)
        data[:, 0] = frames
        data[:, 1] = identities
        data[:, 2] = xtls
        data[:, 3] = ytls
        data[:, 4] = widths
        data[:, 5] = heights

        return data

    def _is_motion(self, frame: int, identity: int, data: np.ndarray):
        if frame == 1:
            # First frame, it is motion
            return True

        selector = np.logical_and(data[:, 0] == frame, data[:, 1] == identity)
        idx = np.argmax(selector)

        previous_data = data[:idx, :]

        # Can we find it in the previous frame
        previous_selector = np.logical_and(
            previous_data[:, 0] == frame - 1, previous_data[:, 1] == identity
        )
        if not np.any(previous_selector):
            # We didn't see this item last frame
            return True
        previous_idx = np.argmax(previous_selector)

        centroid = data[idx, 2:4] + data[idx, 4:6]
        previous_centroid = (
            previous_data[previous_idx, 2:4] + previous_data[previous_idx, 4:6]
        )

        length = np.linalg.norm(centroid - previous_centroid)

        return length >= 2

    def _generate_gt(
        self, xml: str, start: int, end: int, motion_only: bool, dataset_path: str
    ):
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

            for frame in unique_frames:
                for identity in unique_identities:
                    selector = np.logical_and(
                        data[:, 0] == frame, data[:, 1] == identity
                    )

                    if not np.any(selector):
                        continue

                    idx = np.argmax(selector)
                    if not self._is_motion(frame, identity, data):
                        data = np.delete(data, idx, axis=0)

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

        self._generate_img(args.video, args.start, args.end, dataset_path)
        self._generate_gt(
            args.xml, args.start, args.end, args.enable_motion_only, dataset_path
        )
