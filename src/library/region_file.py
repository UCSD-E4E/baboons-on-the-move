from abc import ABC
from sqlite3 import connect
from typing import Iterator
import pandas as pd
from baboon_tracking.models.region import Region
from os.path import basename, splitext
import numpy as np


class RegionFile(ABC):
    def __init__(self):
        self._frame = 0
        self._max_frame = 0

    def __iter__(self):
        self._frame = 0
        self._max_frame = 0
        return self

    def __next__(self):
        if not self._max_frame:
            self._max_frame = self._get_max_frame()

        self._frame += 1

        if self._frame <= self._max_frame:
            return self.frame_regions(self._frame)
        else:
            raise StopIteration

    def _get_max_frame(self) -> int:
        raise Exception("abstract method")

    def frame_regions(self, frame: int) -> Iterator[Region]:
        raise Exception("abstract method")


class GroundTruthTextRegionFile(RegionFile):
    def __init__(self, file_name: str):
        super().__init__()
        self.array = pd.read_csv(file_name).to_numpy()

    def _get_max_frame(self) -> int:
        return np.max(self.array[:, 0])

    def frame_regions(self, frame: int) -> Iterator[Region]:
        frame_regions = self.array[self.array[:, 0] == frame, 1:6]
        for identity, x1, y1, width, height in frame_regions:
            x2 = x1 + width
            y2 = y1 + height

            yield Region((x1, y1, x2, y2), id_str=str(identity), identity=identity)


class SqliteRegionFile(RegionFile):
    def __init__(self, file_name: str) -> None:
        super().__init__()

        self._connection = connect(file_name)
        self._cursor = self._connection.cursor()

    def _get_max_frame(self) -> int:
        return next(
            self._cursor.execute(
                """
            SELECT MAX(frame) FROM regions
            """
            )
        )[0] or 0

    def frame_regions(self, frame: int) -> Iterator[Region]:
        for x1, y1, x2, y2, id_str, identity in self._cursor.execute(
            """
            SELECT x1, y1, x2, y2, id_str, identity FROM regions
            WHERE frame = ?
            """,
            (frame,),
        ):
            yield Region((x1, y1, x2, y2), id_str=id_str, identity=identity)


def region_factory(input_file: str) -> RegionFile:
    if basename(input_file) == "gt.txt":
        return GroundTruthTextRegionFile(input_file)
    elif splitext(input_file)[1] == ".db":
        return SqliteRegionFile(input_file)

    raise Exception("File type for region file not recognized.")
