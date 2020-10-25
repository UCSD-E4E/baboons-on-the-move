"""
Lints all the Python files.
"""
import os
import subprocess

from cli_plugins.utils import execute_node_script, get_python_files


def lint():
    """
    Lints all the Python files.
    """
    if os.getenv("CLI_ACTIVE"):
        from pylint.lint import Run  # pylint: disable=import-outside-toplevel

        python_files = get_python_files()

        for f in python_files:
            subprocess.check_call(["black", "--check", f])

        Run(python_files)
        execute_node_script("pyright")
    else:
        os.environ["CLI_ACTIVE"] = "1"

        subprocess.check_call(
            ["poetry", "run", "python", "./cli.py", "lint"], shell=True
        )
