"""
Manages encryption and decryption.
"""
from argparse import ArgumentParser, Namespace
import getpass
import os
import pyAesCrypt

from cli_plugins.cli_plugin import CliPlugin


BUFFER_SIZE = 64 * 1024


def _get_password():
    password = os.getenv("ENCRYPTION_KEY")
    if not password:
        password = getpass.getpass(prompt="Encryption Key: ")

    return password


class Encrypt(CliPlugin):
    """
    Encrypts all files in the ./decrypted folder.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        password = _get_password()

        files = [
            f
            for f in os.listdir("./decrypted")
            if os.path.isfile(os.path.join("./decrypted", f))
        ]

        for file in files:
            pyAesCrypt.encryptFile(
                os.path.join("./decrypted", file),
                os.path.join("./encrypted", file + ".aes"),
                password,
                BUFFER_SIZE,
            )


class Decrypt(CliPlugin):
    """
    Decrypt all the files in the encrypted folder.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        if not os.path.exists("./decrypted"):
            os.makedirs("./decrypted")

        password = _get_password()

        files = [
            f
            for f in os.listdir("./encrypted")
            if os.path.isfile(os.path.join("./encrypted", f))
        ]

        for file in files:
            pyAesCrypt.decryptFile(
                os.path.join("./encrypted", file),
                os.path.join("./decrypted", file.replace(".aes", "")),
                password,
                BUFFER_SIZE,
            )
