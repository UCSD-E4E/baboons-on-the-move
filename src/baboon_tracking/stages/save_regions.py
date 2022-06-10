"""
Base class for saving regions to Sqlite database.
"""

from typing import List
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.models.region import Region
from baboon_tracking.stages.sqlite_base import SqliteBase

from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("baboons")
@stage("frame")
class SaveRegions(SqliteBase):
    """
    Base class for saving regions to Sqlite database.
    """

    def __init__(self, baboons: BaboonsMixin, frame: FrameMixin) -> None:
        SqliteBase.__init__(self)

        self._baboons = baboons
        self._frame = frame

    def on_database_create(self) -> None:
        super().on_database_create()

        SqliteBase.cursor.execute("DROP TABLE IF EXISTS regions")
        SqliteBase.cursor.execute(
            """CREATE TABLE regions (
                x1 int,
                y1 int,
                x2 int,
                y2 int,
                identity int,
                id_str text,
                frame int
            )"""
        )

        self.connection.commit()

    def before_database_close(self) -> None:
        self.save_hash("SaveRegions")

    def execute(self) -> StageResult:
        frame_number = self._frame.frame.get_frame_number()
        self._save_baboons_for_frame(self._baboons.baboons, frame_number)

        return StageResult(True, True)

    def _save_baboons_for_frame(self, baboons: List[Region], frame_number: int):
        baboons = [(b.rectangle, b.id_str, b.identity) for b in baboons]
        baboons = [
            (
                x1,
                y1,
                x2,
                y2,
                identity,
                id_str,
                frame_number,
            )
            for (x1, y1, x2, y2), id_str, identity in baboons
        ]
        baboons.sort(key=lambda b: b[0])
        SqliteBase.cursor.executemany(
            "INSERT INTO regions VALUES (?, ?, ?, ?, ?, ?, ?)",
            baboons,
        )

        for baboon in baboons:
            for data in baboon[:4]:
                self.md5.update(str(data).encode())
