"""
CLI plugin for creating baselines for tests.
"""
from argparse import ArgumentParser, Namespace
from datetime import datetime
from inspect import getmembers, isclass
from os import listdir
from os.path import join
import pathlib
import socket

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import baseline

from cli_plugins.cli_plugin import CliPlugin
from cli_plugins.utils import (
    get_ci_data_folder,
    get_drive_file,
    get_team_drive,
    load_google_drive_creds,
)


class Baseline(CliPlugin):
    """
    CLI plugin for creating baselines for tests.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        curr_date = datetime.now()
        folder_name = "./data/tests/baselines/" + curr_date.strftime("%Y%m%d-%H%M%S")
        pathlib.Path(folder_name).mkdir(exist_ok=True)

        baseline_plugins = [m() for _, m in getmembers(baseline, isclass)]
        for plugin in baseline_plugins:
            plugin.execute(folder_name)

        socket.setdefaulttimeout(600)
        creds = load_google_drive_creds()
        service = build("drive", "v3", credentials=creds)
        drive = get_team_drive(service)
        data_folder = get_ci_data_folder(drive, service)
        tests_folder = get_drive_file("tests", data_folder["id"], drive["id"], service)
        baselines_folder = get_drive_file(
            "baselines", tests_folder["id"], drive["id"], service
        )

        folder_metadata = {
            "name": curr_date.strftime("%Y%m%d-%H%M%S"),
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [baselines_folder["id"]],
            "driveId": drive["id"],
        }
        baseline_folder = (
            # pylint: disable=maybe-no-member"
            service.files()
            .create(
                body=folder_metadata,
                fields="id",
                supportsAllDrives=True,
                supportsTeamDrives=True,
            )
            .execute()
        )

        for file in listdir(folder_name):
            file_metadata = {
                "name": file,
                "parents": [baseline_folder["id"]],
                "driveId": drive["id"],
            }
            media = MediaFileUpload(join(folder_name, file))
            # pylint: disable=maybe-no-member"
            service.files().create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
                supportsTeamDrives=True,
            ).execute()

        with open("baseline.txt", "w") as f:
            f.write(curr_date.strftime("%Y%m%d-%H%M%S"))
