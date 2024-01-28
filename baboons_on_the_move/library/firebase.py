"""
The module is useful for interacting with Firebase.
"""

import json
from os.path import exists
from typing import Any

import firebase_admin
from firebase_admin import credentials, db


DISABLE_NETWORK = False


class MockFirebaseReference:
    def __init__(self, path: str, data: Any):
        self._path = path
        self._data = data

    def child(self, path: str):
        return MockFirebaseReference(f"{self._path}/{path}", self._data)

    def get(self):
        parts = [p for p in self._path.split("/") if p]
        data = self._data

        for part in parts:
            data = data[part]

        return data


class MockFirebaseDB:
    def __init__(self, path: str):
        with open(path, "r", "utf8") as f:
            self._data = json.loads(str.join("\n", f.readlines()))

    def reference(self, path: str):
        return MockFirebaseReference(f"/{path}", self._data)


def initialize_app(disable_network=False):
    """
    Logic for initializing the firebase database app.
    """

    global DISABLE_NETWORK
    DISABLE_NETWORK = disable_network

    if not DISABLE_NETWORK:
        try:
            cred = credentials.Certificate("decrypted/firebase-key.json")
            firebase_admin.initialize_app(
                cred,
                {
                    "databaseURL": "https://baboon-cli-1598770091002-default-rtdb.firebaseio.com/"
                },
            )
        except ValueError:
            pass

        return db
    elif exists("./data/firebase.json"):
        return MockFirebaseDB("./data/firebase.json")
    else:
        return None


def get_dataset_ref(dataset_name: str, parent_ref: db.Reference):
    """
    Navigates down the tree in firebase based off of the dataset name to return the node.
    """

    ref = parent_ref
    for part in dataset_name.split("/"):
        ref = ref.child(part)

    return ref
