"""
Plugin for calculating metrics.
"""
from argparse import ArgumentParser, Namespace
from datetime import datetime

from firebase_admin import db
from pygit2 import Repository

from cli_plugins.cli_plugin import CliPlugin
from library.firebase import initialize_app
from library.metrics import get_metrics
from config import get_latest_config, set_config


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

        initialize_app()
        config, _, _ = get_latest_config()
        set_config(config)

        time = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        ref = db.reference("metrics")
        video_ref = ref.child("input")
        branch_ref = video_ref.child(Repository(".").head.shorthand)
        date_ref = branch_ref.child(time)

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
