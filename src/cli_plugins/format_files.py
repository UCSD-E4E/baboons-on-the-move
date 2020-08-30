"""
Formats all Python files.
"""
import subprocess

from cli_plugins.utils import get_python_files


def format_files():
    """
    Formats all Python files.
    """

    python_files = get_python_files()

    for python_file in python_files:
        subprocess.check_call(["black", python_file])
