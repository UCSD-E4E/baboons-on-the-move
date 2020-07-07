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

GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    parser = argparse.ArgumentParser(description='Baboon Command Line Interface')

    subparsers = parser.add_subparsers()

    code_parser = subparsers.add_parser('code')
    code_parser.set_defaults(func=vscode)

    data_parser = subparsers.add_parser('data')
    data_parser.set_defaults(func=data)

    lint_parser = subparsers.add_parser('lint')
    lint_parser.set_defaults(func=lint)

    shell_parser = subparsers.add_parser('shell')
    shell_parser.set_defaults(func=shell)

    vscode_parser = subparsers.add_parser('vscode')
    vscode_parser.set_defaults(func=vscode)

    res = parser.parse_args()

    res.func()

def _check_vscode_plugin(plugin: str):
    with os.popen('code --list-extensions') as f:
        installed = any([l.strip() == plugin for l in f.readlines()])

    return installed

def _download_file_from_drive(id: str, path: str, service):
    from googleapiclient.http import MediaIoBaseDownload
    request = service.files().get_media(fileId=id)

    with open(path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

def _ensure_vscode_plugin(plugin: str):
    if not _check_vscode_plugin(plugin):
        subprocess.check_call(['code', '--install-extension', plugin], shell=True)

def _extract(path: str, target: str):
    extensions = pathlib.Path(path).suffixes
    extension = ''.join(extensions)

    if extension == '.zip':
        archive = zipfile.ZipFile(path, 'r')
    elif extension == 'tar.gz'or extension == 'tar.xz':
        archive = tarfile.TarFile(path, 'r')

    archive.extractall(target)
    archive.close()

def _get_drive_folder_children(parent_id: str, drive_id: str, service):
    page_token = None

    files = []
    while True:
        results = service.files().list(
            pageSize=10,
            fields='nextPageToken, files(id, name, parents)',
            corpora='drive', driveId=drive_id,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            q="'" + parent_id + "' in parents",
            pageToken=page_token
        ).execute()

        files += results.get('files', [])

        if 'nextPageToken' not in results:
            break

        page_token = results['nextPageToken']

    return files

def _get_drive_file(name: str, parent_id: str, drive_id: str, service):
    page_token = None

    while True:
        results = service.files().list(
            pageSize=10,
            fields='nextPageToken, files(id, name, parents)',
            corpora='drive', driveId=drive_id,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            q="'" + parent_id + "' in parents and name = '" + name + "'",
            pageToken=page_token
        ).execute()

        files = results.get('files', [])

        if 'nextPageToken' not in results:
            break

        page_token = results['nextPageToken']

    if len(files):
        return files[0]

def _get_node_executable(name: str):
    if sys.platform == 'win32':
        executable = name + '.cmd'
    elif sys.platform == 'darwin' or sys.platform == 'linux' or sys.platform == 'linux2':
        executable = name

    if sys.platform == 'win32':
        directory = 'node-v12.18.2-win-x64'
    elif sys.platform == 'darwin':
        directory = 'node-v12.18.2-darwin-x64'
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        directory = 'node-v12.18.2-linux-x64'

    return os.path.realpath('./tools/node/' + directory + '/' + executable)

def _install_node_in_repo():
    if sys.platform == 'win32':
        # Assume we are on 64 bit Intel
        url = 'https://nodejs.org/dist/v12.18.2/node-v12.18.2-win-x64.zip'
        ext = 'zip'
    elif sys.platform == 'darwin':
        # Assume we are on 64 bit Intel
        url = 'https://nodejs.org/dist/v12.18.2/node-v12.18.2-darwin-x64.tar.gz'
        ext = 'tar.gz'
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        # Assume we are on 64 bit Intel
        url = 'https://nodejs.org/dist/v12.18.2/node-v12.18.2-linux-x64.tar.xz'
        ext = 'tar.xz'

    pathlib.Path('./tools').mkdir(exist_ok=True)

    node_archive = './tools/node.' + ext
    node_path = './tools/node'
    if not os.path.exists(node_archive):
        urllib.request.urlretrieve(url, node_archive)

    if not os.path.exists(node_path):
        _extract(node_archive, node_path)

        return True

    return False

def _is_executable_in_path(executable: str):
    if sys.platform == 'win32':
        whichExecutable = 'where'
    elif sys.platform == 'darwin' or sys.platform == 'linux' or sys.platform == 'linux2':
        return False

    which = subprocess.Popen(whichExecutable + ' ' + executable, stdout = subprocess.PIPE)
    _ = which.communicate()

    return which.returncode == 0

def _load_google_drive_creds():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None

    if os.path.exists('google_drive_token.pickle'):
        with open('google_drive_token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_drive_credentials.json', GOOGLE_DRIVE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open('google_drive_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def data():
    from googleapiclient.discovery import build

    pathlib.Path('./data').mkdir(exist_ok=True)

    creds = _load_google_drive_creds()

    service = build('drive', 'v3', credentials=creds)
    results = service.drives().list(
        fields='nextPageToken, drives(id, name)'
    ).execute()
    drive = [d for d in results.get('drives', []) if d['name'] == 'E4E_Aerial_Baboons'][0]

    ci_folder = _get_drive_file('CI', drive['id'], drive['id'], service)
    data_folder = _get_drive_file('data', ci_folder['id'], drive['id'], service)

    data_files = _get_drive_folder_children(data_folder['id'], drive['id'], service)

    for data_file in data_files:
        _download_file_from_drive(data_file['id'], './data/' + data_file['name'], service)

def lint():
    from pylint.lint import Run

    repo_directory = os.path.dirname(os.path.realpath(__file__))
    python_files = [f for f in glob.iglob(repo_directory + '/**/*.py', recursive=True) if os.path.realpath('./tools/node') not in f]

    Run(python_files)
    subprocess.check_call(_get_node_executable('pyright'))

def shell():
    if not _is_executable_in_path('poetry'):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pipx'])
        subprocess.check_call([sys.executable, '-m', 'pipx', 'install', 'poetry'])
        subprocess.check_call([sys.executable, '-m', 'pipx', 'ensurepath'])

    if _install_node_in_repo():
        subprocess.check_call([_get_node_executable('npm'), 'install', '-g', 'pyright'])

    subprocess.check_call(['poetry', 'install'])
    subprocess.check_call(['poetry', 'shell'])

def vscode():
    _ensure_vscode_plugin('eamodio.gitlens')
    _ensure_vscode_plugin('ms-python.python')
    _ensure_vscode_plugin('ms-python.vscode-pylance')
    _ensure_vscode_plugin('VisualStudioExptTeam.vscodeintellicode')

    os.popen('code .')

if __name__ == '__main__':
    main()
