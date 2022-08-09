"""
This module contains a set of methods that are shared between multiple subcommands.
"""
import glob
import os
import subprocess
import sys
import platform
from typing import List


def _get_node_executable(name: str):
    platform_machine = platform.machine()
    is_linux = sys.platform in ("linux", "linux2")
    is_amd64 = platform_machine == "x86_64"

    if sys.platform == "win32":
        executable = name + ".cmd"
    elif sys.platform in ("darwin", "linux", "linux2"):
        executable = name
    else:
        executable = None

    if is_linux:
        directory = f"node-v16.15.1-linux-{'x64' if is_amd64 else 'arm64'}/bin"
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
        and os.path.realpath("./src/third_party") not in f
        and f != os.path.realpath("./src/main.py")
    ]
