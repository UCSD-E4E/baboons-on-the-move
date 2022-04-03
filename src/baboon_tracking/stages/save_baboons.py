"""
Saves the list of baboons in CSV format.
"""
from os import remove
from os.path import exists
from sqlite3 import connect

from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from pipeline import Stage
from pipeline.decorators import stage
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

        self.__enter__()

    def __del__(self):
        self.on_destroy()

    def __enter__(self):
        if self._connection is None:
            if exists("./output/baboons.db"):
                remove("./output/baboons.db")

            self._connection = connect("./output/baboons.db")
            self._cursor = self._connection.cursor()

            self._cursor.execute(
                """CREATE TABLE baboons
               (x1 int, y1 int, x2 int, y2 int, frame int)"""
            )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.on_destroy()

    def execute(self) -> StageResult:
        frame_number = self._frame.frame.get_frame_number()

        baboons = [b.rectangle for b in self._baboons.baboons]
        baboons = [(x1, y1, x2, y2, frame_number) for x1, y1, x2, y2 in baboons]
        self._cursor.executemany("INSERT INTO baboons VALUES (?, ?, ?, ?, ?)", baboons)

        return StageResult(True, True)

    def on_destroy(self) -> None:
        if self._connection is not None:
            self._connection.commit()
            self._connection.close()

            self._cursor = None
            self._connection = None
