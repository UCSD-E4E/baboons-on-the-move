"""
Saves the list of baboons in CSV format.
"""
from datetime import datetime
from os import remove
from os.path import exists
from sqlite3 import connect
import json
import git

from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from config import get_config
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.parent_stage import ParentStage
from pipeline.stage_result import StageResult


@stage("baboons")
@stage("frame")
@stage("capture")
@stage("transformation_matricies")
class SaveBaboons(Stage):
    """
    Saves the list of baboons in CSV format.
    """

    def __init__(
        self,
        baboons: BaboonsMixin,
        frame: FrameMixin,
        capture: CaptureMixin,
        transformation_matricies: TransformationMatricesMixin,
    ) -> None:
        Stage.__init__(self)

        self._baboons = baboons
        self._frame = frame
        self._capture = capture
        self._transformation_matricies = transformation_matricies

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
               (
                   x1 int,
                   y1 int,
                   x2 int,
                   y2 int,
                   t11 real, t12 real, t13 real,
                   t21 real, t22 real, t23 real,
                   t31 real, t32 real, t33 real,
                   frame int)"""
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
                    ("file_name", self._capture.name),
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
        T = self._transformation_matricies.current_frame_transformation

        baboons = [b.rectangle for b in self._baboons.baboons]
        baboons = [
            (
                x1,
                y1,
                x2,
                y2,
                T[0, 0],
                T[0, 1],
                T[0, 2],
                T[1, 0],
                T[1, 1],
                T[1, 2],
                T[2, 0],
                T[2, 1],
                T[2, 2],
                frame_number,
            )
            for x1, y1, x2, y2 in baboons
        ]
        self._cursor.executemany(
            "INSERT INTO motion_regions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            baboons,
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
