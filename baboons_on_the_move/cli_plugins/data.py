"""
Gets the data necessary to test the algorithm from Google Drive.
"""
import pathlib
from argparse import ArgumentParser, Namespace

from bom_common.pluggable_cli import Plugin
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm

from baboons_on_the_move.cli_plugins.utils_import import (
    get_ci_data_folder,
    get_team_drive,
    load_google_drive_creds,
)


class Data(Plugin):
    """
    Gets the data necessary to test the algorithm from Google Drive.
    """

    def __init__(self, parser: ArgumentParser):
        super().__init__(parser)

    def execute(self, args: Namespace):
        pathlib.Path("./data").mkdir(exist_ok=True)

        creds = load_google_drive_creds()
        service = build("drive", "v3", credentials=creds)
        drive = get_team_drive(service)
        data_folder = get_ci_data_folder(drive, service)

        self._download_files_from_drive(
            data_folder["id"], drive["id"], "./data", service
        )

    def _download_files_from_drive(
        self, folder_id: str, drive_id: str, path: str, service
    ):
        data_files = self._get_drive_folder_children(folder_id, drive_id, service)

        for data_file in data_files:
            if data_file["mimeType"] == "application/vnd.google-apps.folder":
                folder_path = path + "/" + data_file["name"]
                pathlib.Path(folder_path).mkdir(exist_ok=True)

                self._download_files_from_drive(
                    data_file["id"], drive_id, folder_path, service
                )
            else:
                self._download_file_from_drive(
                    data_file["id"],
                    data_file["name"],
                    path + "/" + data_file["name"],
                    service,
                )

    def _download_file_from_drive(self, identity: str, name: str, path: str, service):
        print('Downloading "' + name + '" to "' + path + '"')

        request = service.files().get_media(fileId=identity)

        with open(path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)

            done = False
            with tqdm() as pbar:
                while done is False:
                    progress, done = downloader.next_chunk()

                    pbar.total = progress.total_size
                    pbar.update(progress.resumable_progress)

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

        return [
            service.files()
            .get(
                fileId=file["id"],
                supportsTeamDrives=True,
                supportsAllDrives=True,
            )
            .execute()
            for file in files
        ]
