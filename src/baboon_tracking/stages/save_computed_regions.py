"""
Saves the computed, identity regions into a Sqlite database.
"""

from sqlite3 import OperationalError
from typing import Dict, List, Tuple
import backoff
from baboon_tracking.mixins.particle_filter_history_mixin import (
    ParticleFilterHistoryMixin,
)
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.stages.sqlite_base import SqliteBase
from baboon_tracking.models.particle_filter import Particle
from bom_pipeline.decorators import stage
from bom_pipeline.stage_result import StageResult
from library.utils import flatten


@stage("baboons")
@stage("particle_filter_history")
@stage("frame")
class SaveComputedRegions(SqliteBase):
    """
    Saves the computed, identity regions into a Sqlite database.
    """

    def __init__(
        self,
        baboons: BaboonsMixin,
        particle_filter_history: ParticleFilterHistoryMixin,
        frame: FrameMixin,
    ) -> None:
        SqliteBase.__init__(self)

        self._baboons = baboons
        self._particle_filter_history = particle_filter_history
        self._frame = frame
        self._particle_filter_history_idx: Dict[int, int] = {}

    def before_database_close(self) -> None:
        self.save_hash("SaveComputedRegions")

    @backoff.on_exception(backoff.expo, OperationalError)
    def on_database_create(self) -> None:
        SqliteBase.cursor.execute("DROP TABLE IF EXISTS bayesian_filter_regions")
        SqliteBase.cursor.execute("DROP TABLE IF EXISTS particle_filter_history")

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

        SqliteBase.cursor.execute(
            """CREATE TABLE particle_filter_history (
                filter_identity int,
                step_name text,
                x1 int,
                y1 int,
                x2 int,
                y2 int,
                identity int,
                id_str text,
                observed int,
                weight float,
                frame int
            )"""
        )

        self.connection.commit()

    @backoff.on_exception(backoff.expo, OperationalError)
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

        particle_filters: List[Tuple[int, str, Particle]] = flatten(
            flatten(
                [
                    [
                        [
                            (
                                filter_idx,
                                step_name,
                                p.baboon.rectangle[0],
                                p.baboon.rectangle[1],
                                p.baboon.rectangle[2],
                                p.baboon.rectangle[3],
                                p.baboon.identity,
                                p.baboon.id_str,
                                p.baboon.observed,
                                p.weight,
                                frame_number,
                            )
                            for p in particles
                        ]
                        for step_idx, step_name, particles in f
                        if filter_idx not in self._particle_filter_history_idx
                        or self._particle_filter_history_idx[filter_idx] > step_idx
                    ]
                    for filter_idx, f in self._particle_filter_history.particle_filter_history
                ]
            )
        )

        SqliteBase.cursor.executemany(
            "INSERT INTO particle_filter_history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            particle_filters,
        )

        SqliteBase.connection.commit()

        return StageResult(True, True)
