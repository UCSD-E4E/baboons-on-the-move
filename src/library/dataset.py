"""
Module for getting data from the NAS.
"""

import pickle
import sys
from os import getenv, makedirs
import getpass
import json
from genericpath import exists, isdir
from synology_api import filestation
from tqdm import tqdm


def _download_folder(
    synology_path: str, target_dir: str, file_station: filestation.FileStation
):
    makedirs(target_dir, exist_ok=True)

    files_and_dirs = file_station.get_file_list(synology_path)["data"]["files"]
    dirs = [fd for fd in files_and_dirs if fd["isdir"]]

    for directory in dirs:
        _download_folder(
            directory["path"], f"{target_dir}/{directory['name']}", file_station
        )

    files = [fd for fd in files_and_dirs if not fd["isdir"]]

    for file in tqdm(files):
        file_station.get_file(file["path"], "download", dest_path=f"{target_dir}")


def _get_credentials():
    username = getenv("NAS_USER_NAME")
    password = getenv("NAS_PASSWORD")

    username_token = None
    password_token = None
    if exists("./nas_token.pickle"):
        with open("./nas_token.pickle", "rb") as f:
            username_token, password_token = pickle.load(f)

    if not username:
        if username_token:
            username = username_token
        else:
            print("NAS Username: ", end="")
            username = sys.stdin.readline().strip()

    if not password:
        if password_token:
            password = password_token
        else:
            password = getpass.getpass(prompt="NAS Password: ")

    with open("./nas_token.pickle", "wb") as f:
        pickle.dump((username, password), f)

    return username, password


def _get_nas_parameters():
    username, password = _get_credentials()
    with open("./decrypted/nas.json", "r", encoding="utf8") as f:
        nas_config = json.load(f)
        hostname = nas_config["hostname"]
        port = nas_config["port"]

    return username, password, hostname, port


def get_dataset_path(name: str):
    """
    Gets the path for the named dataset, downloads it if necessary.
    """

    dataset_root = f"./data/Datasets/{name}"

    if not isdir(dataset_root):
        username, password, hostname, port = _get_nas_parameters()

        file_station = filestation.FileStation(
            hostname,
            port,
            username,
            password,
            secure=True,
            cert_verify=False,
            dsm_version=2,
            debug=False,
            otp_code=None,
        )

        _download_folder(f"/baboons/Datasets/{name}", dataset_root, file_station)

    return f"{dataset_root}/img"


def _find_leaf_nodes(path: str, file_station: filestation.FileStation):
    files_and_dirs = file_station.get_file_list(path)["data"]["files"]
    dirs = [fd for fd in files_and_dirs if fd["isdir"]]
    files = [fd for fd in files_and_dirs if not fd["isdir"]]

    leaf_nodes = [f["path"] for f in files]
    for directory in dirs:
        leaf_nodes.extend(_find_leaf_nodes(directory["path"], file_station))

    return leaf_nodes


def get_dataset_list(root: str = ""):
    cache_path = "./dataset_cache.pickle"

    if exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    username, password, hostname, port = _get_nas_parameters()

    file_station = filestation.FileStation(
        hostname,
        port,
        username,
        password,
        secure=True,
        cert_verify=False,
        dsm_version=2,
        debug=False,
        otp_code=None,
    )

    leaf_nodes = _find_leaf_nodes(f"/baboons/Datasets/{root}", file_station)

    viso_datasets = set("/".join(l.split("/")[:-1]) for l in leaf_nodes)
    viso_datasets = [
        "/".join(d.split("/")[3:-1]) for d in viso_datasets if d.endswith("img")
    ]

    with open(cache_path, "wb") as f:
        pickle.dump(viso_datasets, f)

    return viso_datasets
