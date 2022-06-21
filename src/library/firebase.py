"""
The module is useful for interacting with Firebase.
"""

import firebase_admin
from firebase_admin import credentials, db


def initialize_app():
    """
    Logic for initializing the firebase database app.
    """
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


def get_dataset_ref(dataset_name, parent_ref: db.Reference):
    ref = parent_ref
    for part in dataset_name.split("/"):
        ref = ref.child(part)

    return ref
