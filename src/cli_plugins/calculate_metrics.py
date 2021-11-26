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

        video_file = "input"
        branch_name = Repository(".").head.shorthand.replace("/", "__slash__")

        initialize_app()
        config, _, _ = get_latest_config()
        set_config(config)

        time = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        ref = db.reference("metrics")

        video_files_ref = ref.child("video_files")
        video_files = video_files_ref.get()
        video_files = list(video_files) if video_files else []

        if video_file not in video_files:
            video_files.append(video_file)
            video_files_ref.set(video_files)

        video_ref = ref.child(video_file)
        branch_ref = video_ref.child(branch_name)
        date_ref = branch_ref.child(time)

        date_ref.set(
            {
                "metrics": [
                    {
                        "true_positive": m.true_positive,
                        "false_positive": m.false_positive,
                        "false_negative": m.false_negative,
                    }
                    for m in get_metrics()
                ],
                "metric_types": ["true_positive", "false_positive", "false_negative"],
                "tags": [],
            }
        )

        branches_ref = video_ref.child("branches")
        branches = branches_ref.get()
        branches = list(branches) if branches else []

        if branch_name not in branches:
            branches.append(branch_name)
            branches_ref.set(branches)

        dates_ref = branch_ref.child("dates")
        dates = dates_ref.get()
        dates = list(dates) if dates else []
        dates.append(time)
        dates_ref.set(dates)

        # latest_ref = video_ref.child("latest")
        # latest_ref.set(time)
