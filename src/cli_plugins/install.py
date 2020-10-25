"""
Installs the necessary dependencies.
"""
import pathlib
import os
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

from cli_plugins.utils import execute_node_script


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


def _install_global_package(package_name: str):
    if os.getenv("VIRTUAL_ENV"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pipx", "--user"])
        subprocess.check_call([sys.executable, "-m", "pipx", "install", package_name])
        subprocess.check_call([sys.executable, "-m", "pipx", "ensurepath"])


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


def install():
    """
    Installs the necessary dependencies.
    """
    if not _is_executable_in_path("poetry"):
        _install_global_package("poetry")

    if not _is_executable_in_path("black"):
        _install_global_package("black")

    if _install_node_in_repo():
        execute_node_script("npm", ["install", "-g", "pyright"])

    subprocess.check_call(["poetry", "install"], shell=True)
