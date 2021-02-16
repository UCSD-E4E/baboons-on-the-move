"""
Plugin for calculating metrics.
"""
from argparse import ArgumentParser, Namespace
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, db

from cli_plugins.cli_plugin import CliPlugin
from library.metrics import get_metrics


class CalculateMetrics(CliPlugin):
    """
    Handles calculating metrics.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def execute(self, args: Namespace):
        """
        Calculate metrics for the specified video and output to Firebase.
        """

        cred = credentials.Certificate("decrypted/firebase-key.json")
        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://baboon-cli-1598770091002-default-rtdb.firebaseio.com/"
            },
        )

        time = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        ref = db.reference("metrics")
        video_ref = ref.child("input")
        date_ref = video_ref.child(time)

        date_ref.set(
            [
                {
                    "true_positive": m.true_positive,
                    "false_positive": m.false_positive,
                    "false_negative": m.false_negative,
                }
                for m in get_metrics()
            ]
        )

        latest_ref = video_ref.child("latest")
        latest_ref.set(time)

        # data_frame = pd.DataFrame(get_metrics())
        # data_frame.to_csv("input_metrics.csv")
