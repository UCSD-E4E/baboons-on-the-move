"""
Manages encryption and decryption.
"""
import getpass
import os
import pyAesCrypt


BUFFER_SIZE = 64 * 1024


def _get_password():
    return getpass.getpass(prompt="Encryption Key: ")


def encrypt():
    """
    Encrypts all files in the ./decrypted folder.
    """
    password = os.getenv("ENCRYPTION_KEY")
    if not password:
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


def decrypt():
    """
    Decrypt all the files in the encrypted folder.
    """
    if not os.path.exists("./decrypted"):
        os.makedirs("./decrypted")

    password = os.getenv("ENCRYPTION_KEY")
    if not password:
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
