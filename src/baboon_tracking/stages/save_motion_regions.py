"""
Saves the list of baboons in Sqlite database.
"""
from os import remove
from os.path import exists
from sqlite3 import OperationalError

import backoff

from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from baboon_tracking.stages.save_regions import SaveRegions
from baboon_tracking.stages.sqlite_base import SqliteBase
from pipeline.decorators import stage
from pipeline.pipeline import Pipeline
from pipeline.stage_result import StageResult


@stage("baboons")
@stage("frame")
@stage("capture")
@stage("transformation_matricies")
class SaveMotionRegions(SaveRegions):
    """
    Saves the list of baboons in Sqlite database.
    """

    def __init__(
        self,
        baboons: BaboonsMixin,
        frame: FrameMixin,
        capture: CaptureMixin,
        transformation_matricies: TransformationMatricesMixin,
    ) -> None:
        SaveRegions.__init__(self, baboons, frame)

        self._capture = capture
        self._transformation_matricies = transformation_matricies

    def __del__(self):
        self.on_destroy()

    def before_database_create(self) -> None:
        if exists(self.file_name):
            remove(self.file_name)

    @backoff.on_exception(backoff.expo, OperationalError)
    def on_database_create(self) -> None:
        super().on_database_create()

        SqliteBase.cursor.execute(
            """CREATE TABLE motion_regions (
                x1 int,
                y1 int,
                x2 int,
                y2 int,
                frame int
            )"""
        )

        SqliteBase.cursor.execute(
            """CREATE TABLE transformations (
                t11 real, t12 real, t13 real,
                t21 real, t22 real, t23 real,
                t31 real, t32 real, t33 real,
                frame int
            )"""
        )

        SqliteBase.connection.commit()

        SqliteBase.insert_metadata(
            {
                "file_name": self._capture.name,
                "frame_height": self._capture.frame_height,
                "frame_width": self._capture.frame_width,
            }
        )

        SqliteBase.connection.commit()

    @backoff.on_exception(backoff.expo, OperationalError)
    def execute(self) -> StageResult:
        stage_result = super().execute()

        frame_number = self._frame.frame.get_frame_number()
        T = self._transformation_matricies.current_frame_transformation

        baboons = [b.rectangle for b in self._baboons.baboons]
        baboons = [
            (
                x1,
                y1,
                x2,
                y2,
                frame_number,
            )
            for x1, y1, x2, y2 in baboons
        ]
        SqliteBase.cursor.executemany(
            "INSERT INTO motion_regions VALUES (?, ?, ?, ?, ?)",
            baboons,
        )
        SqliteBase.cursor.execute(
            "INSERT INTO transformations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
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
            ),
        )

        return stage_result
