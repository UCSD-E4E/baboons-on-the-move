from os.path import exists
from os import unlink
from shutil import copy
from sqlite3 import connect

import cv2
import py7zr
from library.nas import NAS

config_hash = "be663dd4b55518bae23d00859e8b7a22"

datasets = [
    "VISO/car/003",
    "VISO/car/004",
    "VISO/car/005",
    "VISO/car/006",
    "VISO/car/007",
    "VISO/car/008",
    "VISO/car/009",
    "Baboons/NeilThomas/001",
]


def process_directory(dataset: str, dir: str, nas: NAS):
    structure = [
        f"{f}/results.db.7z"
        for f in nas.list_structure(dir)
        if f.split("/")[-1].isnumeric()
    ]

    img = cv2.imread(f"./data/Datasets/{dataset}/img/000001.jpg")
    frame_height, frame_width, _ = img.shape

    for file in structure:
        if exists("./output/results.db.7z"):
            unlink("./output/results.db.7z")

        if exists("./output/results.db"):
            unlink("./output/results.db")

        if nas.exists(f"{file}.bak"):
            continue

        nas.download_file(file, "./output")
        copy("./output/results.db.7z", "./output/results.db.7z.bak")

        with py7zr.SevenZipFile("./output/results.db.7z", "r") as archive:
            archive.extractall()
        unlink("./output/results.db.7z")

        with connect("./output/results.db") as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE metadata
                SET value = ?
                WHERE key = ?
                """,
                (dataset, "file_name"),
            )

            metadata = {
                "frame_height": frame_height,
                "frame_width": frame_width,
            }

            cursor.executemany(
                "INSERT INTO metadata VALUES (?, ?, ?)",
                [("MotionTrackerPipeline", k, v) for k, v in metadata.items()],
            )

        with py7zr.SevenZipFile("./output/results.db.7z", "w") as archive:
            archive.write("./output/results.db")

        nas.upload_file(
            "/".join(file.split("/")[:-1]),
            "./output/results.db.7z",
        )

        nas.upload_file(
            "/".join(file.split("/")[:-1]),
            "./output/results.db.7z.bak",
        )


def bool2str(input: bool):
    if input:
        return "enabled"
    else:
        return "disabled"


nas = NAS()

for dataset in datasets:
    root = f"/baboons/Results/{dataset}/{config_hash}"

    tracking_presets = [(False, False), (True, False), (False, True), (True, True)]

    process_directory(dataset, root, nas)

    exit()

    for track, persist in tracking_presets:
        path = f"{root}/tracking_{bool2str(track)}/persist_{bool2str(persist)}"
        process_directory(dataset, path, nas)
