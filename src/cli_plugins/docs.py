"""
Generates sphinx documentation from source code
"""
import os
import subprocess
import sys


def docs():
    """
    Lints all the Python files.
    """
    if os.getenv("CLI_ACTIVE"):
        subprocess.check_call(["make", "clean"], cwd="./docs/")

        packages = ["baboon_tracking", "pipeline", "scripts"]

        for p in packages:
            subprocess.check_call(
                [
                    "sphinx-apidoc",
                    "-o",
                    os.path.join("./docs/src/", p),
                    os.path.join("./src/", p),
                ]
            )

        subprocess.check_call(["make", "html"], cwd="./docs/")

    else:
        os.environ["CLI_ACTIVE"] = "1"

        subprocess.check_call(
            ["poetry", "run", "python", "./cli.py", "docs"],
            shell=(sys.platform == "win32"),
        )
