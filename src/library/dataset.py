"""
Module for getting data from the NAS.
"""

from os import unlink
import pickle
from genericpath import exists, isdir

import py7zr
from library.nas import NAS


def get_dataset_path(name: str):
    """
    Gets the path for the named dataset, downloads it if necessary.
    """

    dataset_root = f"./data/Datasets/{name}"

    if not isdir(dataset_root):
        nas = NAS()
        nas.download_folder(f"/baboons/Datasets/{name}", dataset_root)

    return dataset_root


def get_dataset_list(root: str = ""):
    cache_path = "./dataset_cache.pickle"

    if exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    nas = NAS()
    leaf_nodes = nas.find_leaf_nodes(f"/baboons/Datasets/{root}")

    viso_datasets = set("/".join(l.split("/")[:-1]) for l in leaf_nodes)
    viso_datasets = [
        "/".join(d.split("/")[3:-1]) for d in viso_datasets if d.endswith("img")
    ]

    with open(cache_path, "wb") as f:
        pickle.dump(viso_datasets, f)

    return viso_datasets


def dataset_motion_results_exists(
    video_file: str,
    idx: int,
    config_hash: str,
):
    nas = NAS()
    return nas.exists(f"/baboons/Results/{video_file}/{config_hash}/{idx}")


def get_dataset_motion_results(
    video_file: str,
    idx: int,
    config_hash: str,
):
    if exists("./output/results.db"):
        unlink("./output/results.db")

    if exists("./output/results.db.7z"):
        unlink("./output/results.db.7z")

    nas = NAS()
    nas.download_file(
        f"/baboons/Results/{video_file}/{config_hash}/{idx}/results.db.7z", "./output"
    )

    with py7zr.SevenZipFile("./output/results.db.7z", "r") as archive:
        archive.extractall()


def save_dataset_motion_results(
    video_file: str,
    idx: int,
    config_hash: str,
):
    with py7zr.SevenZipFile("./output/results.db.7z", "w") as archive:
        archive.write("./output/results.db")

    nas = NAS()
    nas.upload_file(
        f"/baboons/Results/{video_file}/{config_hash}/{idx}",
        "./output/results.db.7z",
    )


def dataset_filter_results_exists(
    video_file: str,
    enable_tracking: bool,
    enable_persist: bool,
    idx: int,
    config_hash: str,
):
    tracking_folder = "tracking_enabled" if enable_tracking else "tracking_disabled"
    persist_folder = "persist_enabled" if enable_persist else "persist_disabled"

    nas = NAS()
    return nas.exists(
        f"/baboons/Results/{video_file}/{config_hash}/{tracking_folder}/{persist_folder}/{idx}"
    )


def get_dataset_filter_results(
    video_file: str,
    enable_tracking: bool,
    enable_persist: bool,
    idx: int,
    config_hash: str,
):
    if exists("./output/results.db"):
        unlink("./output/results.db")

    if exists("./output/results.db.7z"):
        unlink("./output/results.db.7z")

    tracking_folder = "tracking_enabled" if enable_tracking else "tracking_disabled"
    persist_folder = "persist_enabled" if enable_persist else "persist_disabled"

    nas = NAS()
    nas.download_file(
        f"/baboons/Results/{video_file}/{config_hash}/{tracking_folder}/{persist_folder}/{idx}/results.db.7z",
        "./output",
    )

    with py7zr.SevenZipFile("./output/results.db.7z", "r") as archive:
        archive.extractall()


def save_dataset_filter_results(
    video_file: str,
    enable_tracking: bool,
    enable_persist: bool,
    idx: int,
    config_hash: str,
):
    with py7zr.SevenZipFile("./output/results.db.7z", "w") as archive:
        archive.write("./output/results.db")

    tracking_folder = "tracking_enabled" if enable_tracking else "tracking_disabled"
    persist_folder = "persist_enabled" if enable_persist else "persist_disabled"

    nas = NAS()
    nas.upload_file(
        f"/baboons/Results/{video_file}/{config_hash}/{tracking_folder}/{persist_folder}/{idx}",
        "./output/results.db.7z",
    )
