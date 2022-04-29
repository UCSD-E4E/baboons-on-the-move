"""
Saves the list of baboons in CSV format.
"""
from datetime import datetime
from os import remove
from os.path import exists
from sqlite3 import connect
import git
import json

from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from config import get_config
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.parent_stage import ParentStage
from pipeline.stage_result import StageResult


@stage("baboons")
@stage("frame")
class SaveBaboons(Stage):
    """
    Saves the list of baboons in CSV format.
    """

    def __init__(self, baboons: BaboonsMixin, frame: FrameMixin) -> None:
        Stage.__init__(self)

        self._baboons = baboons
        self._frame = frame
        self._connection = None
        self._cursor = None

    def __del__(self):
        self.on_destroy()

    def on_init(self) -> None:
        file_name = "./output/results.db"

        if self._connection is None:
            if exists(file_name):
                remove(file_name)

            self._connection = connect(file_name)
            self._cursor = self._connection.cursor()

            self._cursor.execute(
                """CREATE TABLE motion_regions
               (x1 int, y1 int, x2 int, y2 int, frame int)"""
            )

            self._cursor.execute(
                """CREATE TABLE metadata
                (key text, value text)"""
            )

            self._cursor.execute(
                """CREATE TABLE stages
                (name text, sort_order int)"""
            )

            self._connection.commit()

            repo = git.Repo(".")
            sha = repo.head.object.hexsha

            self._cursor.executemany(
                "INSERT INTO metadata VALUES (?, ?)",
                [
                    ("start_time", datetime.utcnow()),
                    ("git_commit", sha),
                    ("config", json.dumps(get_config())),
                ],
            )

            self._cursor.executemany(
                "INSERT INTO stages VALUES (?, ?)",
                [
                    (s.__class__.__name__, i)
                    for i, s in enumerate(ParentStage.static_stages)
                ],
            )

            self._connection.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        self.on_destroy()

    def execute(self) -> StageResult:
        frame_number = self._frame.frame.get_frame_number()

        baboons = [b.rectangle for b in self._baboons.baboons]
        baboons = [(x1, y1, x2, y2, frame_number) for x1, y1, x2, y2 in baboons]
        self._cursor.executemany(
            "INSERT INTO motion_regions VALUES (?, ?, ?, ?, ?)", baboons
        )

        return StageResult(True, True)

    def on_destroy(self) -> None:
        if self._connection is not None:
            self._connection.commit()

            self._cursor.execute(
                "INSERT INTO metadata VALUES (?, ?)",
                ("end_time", datetime.utcnow()),
            )

            self._connection.commit()
            self._connection.close()

            self._cursor = None
            self._connection = None
