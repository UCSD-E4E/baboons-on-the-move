"""
This module contains a set of methods that are shared between multiple subcommands.
"""
import glob
import os
import pickle
import subprocess
import sys
from typing import Dict, List

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import Resource


GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_node_executable(name: str):
    if sys.platform == "win32":
        executable = name + ".cmd"
    elif (
        sys.platform == "darwin" or sys.platform == "linux" or sys.platform == "linux2"
    ):
        executable = name
    else:
        executable = None

    if sys.platform == "linux" or sys.platform == "linux2":
        directory = "node-v14.15.1-linux-x64/bin"
    else:
        directory = None

    return os.path.realpath("./tools/node/" + directory + "/" + executable)


def execute_node_script(script: str, params=None):
    """
    Executes a global node module.
    """

    if params is None:
        params = []

    params: List[str] = list(params)
    params.insert(0, _get_node_executable(script))
    if sys.platform != "win32":
        params.insert(0, _get_node_executable("node"))

    print(params)

    return subprocess.check_call(params)


def get_python_files():
    """
    Get a list of all of the python files to check for linting.
    """

    repo_directory = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )
    return [
        f
        for f in glob.iglob(repo_directory + "/**/*.py", recursive=True)
        if os.path.realpath("./tools/node") not in f
        and os.path.realpath("./src/baboon_tracking_old") not in f
        and os.path.realpath("./utils") not in f
        and os.path.realpath("./src/scripts") not in f
        and os.path.realpath("./test") not in f
        and os.path.realpath("./docs") not in f
        and f != os.path.realpath("./src/main.py")
    ]


def load_google_drive_creds():
    """
    Load the credential file.
    """
    creds = None

    if os.path.exists("google_drive_token.pickle"):
        with open("google_drive_token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./decrypted/google_drive_credentials.json", GOOGLE_DRIVE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("google_drive_token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def get_team_drive(service: Resource):
    """
    Get the aerial baboons team drive.
    """
    results = (
        service.drives()  # pylint: disable=maybe-no-member
        .list(fields="nextPageToken, drives(id, name)")
        .execute()
    )
    return [d for d in results.get("drives", []) if d["name"] == "E4E_Aerial_Baboons"][
        0
    ]


def get_ci_data_folder(drive: Dict, service: Resource):
    """
    Get the CI/data folder from the drive.
    """
    ci_folder = get_drive_file("CI", drive["id"], drive["id"], service)
    return get_drive_file("data", ci_folder["id"], drive["id"], service)


def get_drive_file(name: str, parent_id: str, drive_id: str, service):
    """
    Get a file from the drive.
    """
    page_token = None

    while True:
        results = (
            service.files()
            .list(
                pageSize=10,
                fields="nextPageToken, files(id, name, parents)",
                corpora="drive",
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                q="'" + parent_id + "' in parents and name = '" + name + "'",
                pageToken=page_token,
            )
            .execute()
        )

        files = results.get("files", [])

        if "nextPageToken" not in results:
            break

        page_token = results["nextPageToken"]

    if files:
        return files[0]
