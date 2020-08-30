import glob
import os
import subprocess
import sys
from typing import List


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


def execute_node_script(script: str, params=None):
    if params is None:
        params = []

    params: List[str] = list(params)
    params.insert(0, _get_node_executable(script))
    params.insert(0, _get_node_executable("node"))

    return subprocess.check_call(params)


def get_python_files():
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
