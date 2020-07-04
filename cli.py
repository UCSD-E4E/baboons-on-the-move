# These are default python packages.  No installed modules here.
import argparse
import glob
import os
import pathlib
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

def main():
    parser = argparse.ArgumentParser(description='Baboon Command Line Interface')

    subparsers = parser.add_subparsers()

    shell_parser = subparsers.add_parser('shell')
    shell_parser.set_defaults(func=shell)

    lint_parser = subparsers.add_parser('lint')
    lint_parser.set_defaults(func=lint)

    vscode_parser = subparsers.add_parser('vscode')
    vscode_parser.set_defaults(func=vscode)

    res = parser.parse_args()

    res.func()

def _ensure_vscode_plugin(plugin: str):
    with os.popen('code --list-extensions') as f:
        installed = any([l.strip() == plugin for l in f.readlines()])

    if not installed:
        os.popen('code --install-extension ' + plugin)

def _extract(path: str, target: str):
    extensions = pathlib.Path(path).suffixes
    extension = ''.join(extensions)

    if extension == '.zip':
        archive = zipfile.ZipFile(path, 'r')
    elif extension == 'tar.gz'or extension == 'tar.xz':
        archive = tarfile.TarFile(path, 'r')

    archive.extractall(target)
    archive.close()

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
        whichExecutable = 'which'

    which = subprocess.Popen(whichExecutable + ' ' + executable, stdout = subprocess.PIPE)
    _ = which.communicate()

    return which.returncode == 0

def shell():
    if not _is_executable_in_path('poetry'):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pipx'])
        subprocess.check_call([sys.executable, '-m', 'pipx', 'install', 'poetry'])
        subprocess.check_call([sys.executable, '-m', 'pipx', 'ensurepath'])

    if _install_node_in_repo():
        subprocess.check_call([_get_node_executable('npm'), 'install', '-g', 'pyright'])

    subprocess.check_call(['poetry', 'install'])
    subprocess.check_call(['poetry', 'shell'])

def lint():
    from pylint.lint import Run

    repo_directory = os.path.dirname(os.path.realpath(__file__))
    python_files = [f for f in glob.iglob(repo_directory + '/**/*.py', recursive=True) if os.path.realpath('./tools/node') not in f]

    Run(python_files)
    subprocess.check_call(_get_node_executable('pyright'))

def vscode():
    _ensure_vscode_plugin('ms-python.python')
    _ensure_vscode_plugin('ms-python.vscode-pylance')

    os.popen('code .')

if __name__ == '__main__':
    main()
