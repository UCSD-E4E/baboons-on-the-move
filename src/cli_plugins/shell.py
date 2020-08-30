import subprocess

from cli_plugins.install import install


def shell():
    """
    Ensures that a venv is setup and that all necessary dependencies are installed.
    Starts a shell in the venv once setup.
    """

    install()

    subprocess.check_call(["poetry", "shell"])
