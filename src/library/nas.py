import json
import pickle
from genericpath import exists
from os import getenv, makedirs
import sys
import getpass
from synology_api import filestation
from tqdm import tqdm


class NAS:
    def __init__(self):
        username, password, hostname, port = self._get_nas_parameters()

        self._file_station = filestation.FileStation(
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

    def _get_credentials(self):
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

    def _get_nas_parameters(self):
        username, password = self._get_credentials()
        with open("./decrypted/nas.json", "r", encoding="utf8") as f:
            nas_config = json.load(f)
            hostname = nas_config["hostname"]
            port = nas_config["port"]

        return username, password, hostname, port

    def find_leaf_nodes(self, path: str):
        files_and_dirs = self._file_station.get_file_list(path)["data"]["files"]
        dirs = [fd for fd in files_and_dirs if fd["isdir"]]
        files = [fd for fd in files_and_dirs if not fd["isdir"]]

        leaf_nodes = [f["path"] for f in files]
        for directory in dirs:
            leaf_nodes.extend(self.find_leaf_nodes(directory["path"]))

        return leaf_nodes

    def download_file(self, synology_path: str, target_dir: str):
        self._file_station.get_file(synology_path, "download", dest_path=target_dir)

    def download_folder(self, synology_path: str, target_dir: str):
        makedirs(target_dir, exist_ok=True)

        files_and_dirs = self._file_station.get_file_list(synology_path)["data"][
            "files"
        ]
        dirs = [fd for fd in files_and_dirs if fd["isdir"]]

        for directory in dirs:
            self.download_folder(directory["path"], f"{target_dir}/{directory['name']}")

        files = [fd for fd in files_and_dirs if not fd["isdir"]]

        for file in tqdm(files):
            self.download_file(file["path"], target_dir)

    def exists(self, path: str) -> bool:
        result = self._file_station.get_file_list(path)

        if "success" not in result:
            return False

        return result["success"]

    def create_folder(self, path: str):
        if self.exists(path):
            return True

        parent = "/".join(path.split("/")[:-1])
        folder = path.split("/")[-1]
        if not self.create_folder(parent):
            return False

        result = self._file_station.create_folder(parent, folder)

        return "success" in result and result["success"]

    def upload_file(self, synology_folder: str, local_file: str):
        self._file_station.upload_file(synology_folder, local_file)