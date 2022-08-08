"""
Module for getting data from the NAS.
"""

import pickle
from genericpath import exists, isdir
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
