"""
Gets the data necessary to test the algorithm from Google Drive.
"""
from argparse import ArgumentParser
import pathlib
import pickle
import os

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tqdm import tqdm

from cli_plugins.cli_plugin import CliPlugin


GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


class Data(CliPlugin):
    """
    Gets the data necessary to test the algorithm from Google Drive.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self):
        pathlib.Path("./data").mkdir(exist_ok=True)

        creds = self._load_google_drive_creds()

        service = build("drive", "v3", credentials=creds)
        results = (
            service.drives()  # pylint: disable=maybe-no-member
            .list(fields="nextPageToken, drives(id, name)")
            .execute()
        )
        drive = [
            d for d in results.get("drives", []) if d["name"] == "E4E_Aerial_Baboons"
        ][0]

        ci_folder = self._get_drive_file("CI", drive["id"], drive["id"], service)
        data_folder = self._get_drive_file(
            "data", ci_folder["id"], drive["id"], service
        )

        data_files = self._get_drive_folder_children(
            data_folder["id"], drive["id"], service
        )

        for data_file in tqdm(data_files, total=len(data_files)):
            self._download_file_from_drive(
                data_file["id"], "./data/" + data_file["name"], service
            )

    def _download_file_from_drive(self, identity: str, path: str, service):
        request = service.files().get_media(fileId=identity)

        with open(path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)

            done = False
            while done is False:
                _, done = downloader.next_chunk()

    def _get_drive_file(self, name: str, parent_id: str, drive_id: str, service):
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

    def _get_drive_folder_children(self, parent_id: str, drive_id: str, service):
        page_token = None

        files = []
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
                    q="'" + parent_id + "' in parents and trashed != true",
                    pageToken=page_token,
                )
                .execute()
            )

            files += results.get("files", [])

            if "nextPageToken" not in results:
                break

            page_token = results["nextPageToken"]

        return files

    def _load_google_drive_creds(self):
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
