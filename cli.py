"""
This module is a CLI for helping with development of the Baboon Tracking Project.
"""

# These are default python packages.  No installed modules here.
import argparse
import glob
import os
import pathlib
import pickle
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
    """
    Main entry point for CLI.
    """

    parser = argparse.ArgumentParser(description="Baboon Command Line Interface")

    subparsers = parser.add_subparsers()

    chart_parser = subparsers.add_parser("chart")
    chart_parser.set_defaults(func=flowchart)

    code_parser = subparsers.add_parser("code")
    code_parser.set_defaults(func=vscode)

    data_parser = subparsers.add_parser("data")
    data_parser.set_defaults(func=data)

    flowchart_parser = subparsers.add_parser("flowchart")
    flowchart_parser.set_defaults(func=flowchart)

    format_parser = subparsers.add_parser("format")
    format_parser.set_defaults(func=format_files)

    install_parser = subparsers.add_parser("install")
    install_parser.set_defaults(func=install)

    lint_parser = subparsers.add_parser("lint")
    lint_parser.set_defaults(func=lint)

    run_parser = subparsers.add_parser("run")
    run_parser.set_defaults(func=run)

    shell_parser = subparsers.add_parser("shell")
    shell_parser.set_defaults(func=shell)

    vscode_parser = subparsers.add_parser("vscode")
    vscode_parser.set_defaults(func=vscode)

    res = parser.parse_args()

    res.func()


def _check_vscode_plugin(plugin: str):
    with os.popen("code --list-extensions") as f:
        installed = any([l.strip() == plugin for l in f.readlines()])

    return installed


def _download_file_from_drive(identity: str, path: str, service):
    from googleapiclient.http import (  # pylint: disable=import-outside-toplevel
        MediaIoBaseDownload,
    )

    request = service.files().get_media(fileId=identity)

    with open(path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)

        done = False
        while done is False:
            _, done = downloader.next_chunk()


def _ensure_vscode_plugin(plugin: str):
    if not _check_vscode_plugin(plugin):
        subprocess.check_call(["code", "--install-extension", plugin], shell=True)


def _extract(path: str, target: str):
    extensions = pathlib.Path(path).suffixes
    extension = "".join(extensions)

    if extension == ".zip":
        archive = zipfile.ZipFile(path, "r")
    elif extension in (".tar.gz", ".tar.xz"):
        archive = tarfile.open(path)
    else:
        archive = None

    archive.extractall(target)
    archive.close()


def _get_drive_folder_children(parent_id: str, drive_id: str, service):
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


def _get_drive_file(name: str, parent_id: str, drive_id: str, service):
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


def _get_node_executable(name: str):
    if sys.platform == "win32":
        executable = name + ".cmd"
    elif (
        sys.platform == "darwin" or sys.platform == "linux" or sys.platform == "linux2"
    ):
        executable = name
    else:
        executable = None

    if sys.platform == "win32":
        directory = "node-v12.18.2-win-x64"
    elif sys.platform == "darwin":
        directory = "node-v12.18.2-darwin-x64/bin"
    elif sys.platform == "linux" or sys.platform == "linux2":
        directory = "node-v12.18.2-linux-x64/bin"
    else:
        directory = None

    return os.path.realpath("./tools/node/" + directory + "/" + executable)


def _get_python_files():
    repo_directory = os.path.dirname(os.path.realpath(__file__))
    return [
        f
        for f in glob.iglob(repo_directory + "/**/*.py", recursive=True)
        if os.path.realpath("./tools/node") not in f
        and os.path.realpath("./src/baboon_tracking_old") not in f
        and os.path.realpath("./utils") not in f
        and os.path.realpath("./src/scripts") not in f
        and os.path.realpath("./test") not in f
        and f != os.path.realpath("./src/main.py")
    ]


def _install_node_in_repo():
    if sys.platform == "win32":
        # Assume we are on 64 bit Intel
        url = "https://nodejs.org/dist/v12.18.2/node-v12.18.2-win-x64.zip"
        ext = "zip"
    elif sys.platform == "darwin":
        # Assume we are on 64 bit Intel
        url = "https://nodejs.org/dist/v12.18.2/node-v12.18.2-darwin-x64.tar.gz"
        ext = "tar.gz"
    elif sys.platform == "linux" or sys.platform == "linux2":
        # Assume we are on 64 bit Intel
        url = "https://nodejs.org/dist/v12.18.2/node-v12.18.2-linux-x64.tar.xz"
        ext = "tar.xz"
    else:
        url = None
        ext = None

    pathlib.Path("./tools").mkdir(exist_ok=True)

    node_archive = "./tools/node." + ext
    node_path = "./tools/node"
    if not os.path.exists(node_archive):
        urllib.request.urlretrieve(url, node_archive)

    if not os.path.exists(node_path):
        _extract(node_archive, node_path)

        return True

    return False


def _is_executable_in_path(executable: str):
    if sys.platform == "win32":
        which_executable = "where"
    elif (
        sys.platform == "darwin" or sys.platform == "linux" or sys.platform == "linux2"
    ):
        return False
    else:
        which_executable = None

    which = subprocess.Popen(
        which_executable + " " + executable, stdout=subprocess.PIPE
    )
    _ = which.communicate()

    return which.returncode == 0


def _load_google_drive_creds():
    from google_auth_oauthlib.flow import (  # pylint: disable=import-outside-toplevel
        InstalledAppFlow,
    )
    from google.auth.transport.requests import (  # pylint: disable=import-outside-toplevel
        Request,
    )

    creds = None

    if os.path.exists("google_drive_token.pickle"):
        with open("google_drive_token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "google_drive_credentials.json", GOOGLE_DRIVE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("google_drive_token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def data():
    """
    Gets the data necessary to test the algorithm from Google Drive.
    """

    from googleapiclient.discovery import (  # pylint: disable=import-outside-toplevel
        build,
    )

    pathlib.Path("./data").mkdir(exist_ok=True)

    creds = _load_google_drive_creds()

    service = build("drive", "v3", credentials=creds)
    results = (
        service.drives()  # pylint: disable=maybe-no-member
        .list(fields="nextPageToken, drives(id, name)")
        .execute()
    )
    drive = [d for d in results.get("drives", []) if d["name"] == "E4E_Aerial_Baboons"][
        0
    ]

    ci_folder = _get_drive_file("CI", drive["id"], drive["id"], service)
    data_folder = _get_drive_file("data", ci_folder["id"], drive["id"], service)

    data_files = _get_drive_folder_children(data_folder["id"], drive["id"], service)

    for data_file in data_files:
        _download_file_from_drive(
            data_file["id"], "./data/" + data_file["name"], service
        )


def flowchart():
    """
    Generates a flowchart representing the baboon tracking algorithm.
    """

    from src.baboon_tracking import (  # pylint: disable=import-outside-toplevel
        BaboonTracker,
    )

    BaboonTracker().flowchart().show()


def format_files():
    """
    Formats all Python files.
    """

    python_files = _get_python_files()

    for python_file in python_files:
        subprocess.check_call(["black", python_file])


def install():
    """
    Installs the necessary dependencies.
    """
    if not _is_executable_in_path("poetry"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pipx"])
        subprocess.check_call([sys.executable, "-m", "pipx", "install", "poetry"])
        subprocess.check_call([sys.executable, "-m", "pipx", "ensurepath"])

    if not _is_executable_in_path("poetry"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pipx"])
        subprocess.check_call([sys.executable, "-m", "pipx", "install", "black"])
        subprocess.check_call([sys.executable, "-m", "pipx", "ensurepath"])

    if _install_node_in_repo():
        subprocess.check_call([_get_node_executable("npm"), "install", "-g", "pyright"])

    subprocess.check_call(["poetry", "install"])


def lint():
    """
    Lints all the Python files.
    """
    if os.getenv("CLI_ACTIVE"):
        from pylint.lint import Run  # pylint: disable=import-outside-toplevel

        python_files = _get_python_files()

        Run(python_files)
        subprocess.check_call(_get_node_executable("pyright"))
    else:
        os.environ["CLI_ACTIVE"] = "1"

        subprocess.check_call(["poetry", "run", "python", "./cli.py", "lint"])


def run():
    """
    Starts the baboon tracker algorithm.
    """

    from src.baboon_tracking import (  # pylint: disable=import-outside-toplevel
        BaboonTracker,
    )

    BaboonTracker().run()


def shell():
    """
    Ensures that a venv is setup and that all necessary dependencies are installed.
    Starts a shell in the venv once setup.
    """

    install()

    subprocess.check_call(["poetry", "shell"])


def vscode():
    """
    Ensures that Visual Studio Code has the necessary Python extensions then launches VS Code.
    """

    _ensure_vscode_plugin("eamodio.gitlens")
    _ensure_vscode_plugin("ms-python.python")
    _ensure_vscode_plugin("ms-python.vscode-pylance")
    _ensure_vscode_plugin("VisualStudioExptTeam.vscodeintellicode")

    os.popen("code .")


if __name__ == "__main__":
    main()
