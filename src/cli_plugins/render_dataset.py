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

        # runtime_config = {
        #     "display": True,
        #     "save": False,
        #     "timings": True,
        #     "progress": True,
        # }

        # DatasetViewerPipeline(
        #     f"{parsed.dataset_path}/img",
        #     parsed.region_file,
        #     runtime_config=runtime_config,
        # ).run()

        # return

        img_path = f"{parsed.dataset_path}/img"

        target_path = f"./output/{parsed.dataset}.mp4"
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

        for img_path in tqdm(imgs):
            frame = int(splitext(basename(img_path))[0])
            img = cv2.imread(img_path)

            for region in parsed.regions.frame_regions(frame):
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
