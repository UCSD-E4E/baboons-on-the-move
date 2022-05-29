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


def get_dataset_path(name: str):
    """
    Gets the path for the named dataset, downloads it if necessary.
    """

    dataset_root = f"./data/Datasets/{name}"

    if not isdir(dataset_root):
        username, password = _get_credentials()
        with open("./decrypted/nas.json", "r", encoding="utf8") as f:
            nas_config = json.load(f)
            hostname = nas_config["hostname"]
            port = nas_config["port"]

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
