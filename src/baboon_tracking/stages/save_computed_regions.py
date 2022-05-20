from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.stages.save_regions_base import SaveRegionsBase
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("baboons")
@stage("frame")
class SaveComputedRegions(SaveRegionsBase):
    def __init__(self, baboons: BaboonsMixin, frame: FrameMixin) -> None:
        SaveRegionsBase.__init__(self, "computed_regions")

        self._baboons = baboons
        self._frame = frame

        self._connection = None
        self._cursor = None

    def on_database_create(self) -> None:
        self.cursor.execute("DROP TABLE IF EXISTS computed_regions")

        self.cursor.execute(
            """CREATE TABLE computed_regions (
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

    def execute(self) -> StageResult:
        frame_number = self._frame.frame.get_frame_number()

        baboons = [(b.rectangle, b.identity, b.id_str) for b in self._baboons.baboons]
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
            for (x1, y1, x2, y2), identity, id_str in baboons
        ]
        self.cursor.executemany(
            "INSERT INTO computed_regions VALUES (?, ?, ?, ?, ?, ?, ?)",
            baboons,
        )

        self.connection.commit()

        return StageResult(True, True)
