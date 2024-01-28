"""
Installs the necessary dependencies.
"""
from argparse import ArgumentParser, Namespace
import pathlib
import os
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
import platform

from shutil import which, copyfile
from cli_plugins.cli_plugin import CliPlugin

from cli_plugins.utils import execute_node_script


def install():
    """
    Installs the necessary dependencies.
    """
    Install(None).execute(None)


class Install(CliPlugin):
    """
    Installs the necessary dependencies.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        if not self._is_executable_in_path("poetry"):
            self._install_global_package("poetry", version="1.5.0")

        if not self._is_executable_in_path("black"):
            self._install_global_package("black")

        if self._install_node_in_repo():
            execute_node_script("npm", ["install", "-g", "pyright"])

    def _extract(self, path: str, target: str):
        extensions = pathlib.Path(path).suffixes
        extension = "".join(extensions)

        with (
            zipfile.ZipFile(path, "r") if extension == ".zip" else tarfile.open(path)
        ) as archive:
            archive.extractall(target)

    def _install_global_package(self, package_name: str, version: str = None):
        if version is None:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )
        else:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", f"{package_name}=={version}"]
            )

    def _install_node_in_repo(self):
        platform_machine = platform.machine()
        is_amd64 = platform_machine == "x86_64"
        is_linux = sys.platform in ("linux", "linux2")

        if is_linux:
            url = f"https://nodejs.org/dist/v16.15.1/node-v16.15.1-linux-{'x64' if is_amd64 else 'arm64'}.tar.xz"
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
            self._extract(node_archive, node_path)

            return True

        return False

    def _is_executable_in_path(self, executable: str):
        return which(executable) is not None
