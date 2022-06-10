"""
Saves the computed, identity regions into a Sqlite database.
"""

from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.stages.sqlite_base import SqliteBase
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("baboons")
@stage("frame")
class SaveComputedRegions(SqliteBase):
    """
    Saves the computed, identity regions into a Sqlite database.
    """

    def __init__(self, baboons: BaboonsMixin, frame: FrameMixin) -> None:
        SqliteBase.__init__(self)

        self._baboons = baboons
        self._frame = frame

    def before_database_close(self) -> None:
        self.save_hash("SaveComputedRegions")

    def on_database_create(self) -> None:
        SqliteBase.cursor.execute("DROP TABLE IF EXISTS bayesian_filter_regions")

        SqliteBase.cursor.execute(
            """CREATE TABLE bayesian_filter_regions (
                x1 int,
                y1 int,
                x2 int,
                y2 int,
                identity int,
                id_str text,
                observed int,
                frame int
            )"""
        )

        self.connection.commit()

    def execute(self) -> StageResult:
        frame_number = self._frame.frame.get_frame_number()

        baboons = [
            (b.rectangle, b.identity, b.id_str, b.observed)
            for b in self._baboons.baboons
        ]
        baboons = [
            (
                int(x1),
                int(y1),
                int(x2),
                int(y2),
                identity,
                id_str,
                observed,
                frame_number,
            )
            for (x1, y1, x2, y2), identity, id_str, observed in baboons
        ]
        baboons.sort(key=lambda b: b[0])
        SqliteBase.cursor.executemany(
            "INSERT INTO bayesian_filter_regions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            baboons,
        )

        for baboon in baboons:
            for data in baboon[:4]:
                self.md5.update(str(data).encode())

        SqliteBase.connection.commit()

        return StageResult(True, True)
