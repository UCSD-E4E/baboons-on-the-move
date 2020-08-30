import os
import subprocess


def _check_vscode_plugin(plugin: str):
    with os.popen("code --list-extensions") as f:
        installed = any([l.strip() == plugin for l in f.readlines()])

    return installed


def _ensure_vscode_plugin(plugin: str):
    if not _check_vscode_plugin(plugin):
        subprocess.check_call(["code", "--install-extension", plugin])


def code():
    """
    Ensures that Visual Studio Code has the necessary Python extensions then launches VS Code.
    """

    _ensure_vscode_plugin("eamodio.gitlens")
    _ensure_vscode_plugin("ms-python.python")
    _ensure_vscode_plugin("ms-python.vscode-pylance")
    _ensure_vscode_plugin("VisualStudioExptTeam.vscodeintellicode")

    os.popen("code .")
