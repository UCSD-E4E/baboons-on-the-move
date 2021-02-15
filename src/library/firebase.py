import firebase_admin
from firebase_admin import credentials


def initialize_app():
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
