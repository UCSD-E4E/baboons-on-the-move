from abc import ABC
from sqlite3 import connect
from typing import Iterator
import pandas as pd
from baboon_tracking.models.region import Region
from os.path import basename, splitext
import numpy as np
from math import ceil, floor
from xml.etree import ElementTree as ET


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
            self._max_frame = self.frame_count

        self._frame += 1

        if self._frame <= self._max_frame:
            return self.frame_regions(self._frame)
        else:
            raise StopIteration

    def to_numpy(self):
        raise Exception("abstract method")

    @property
    def frame_count(self) -> int:
        raise Exception("abstract method")

    @property
    def current_frame(self) -> int:
        return self._frame

    def frame_regions(self, frame: int) -> Iterator[Region]:
        raise Exception("abstract method")


class GroundTruthTextRegionFile(RegionFile):
    def __init__(self, file_name: str):
        super().__init__()
        self.array = pd.read_csv(file_name).to_numpy()

    @property
    def frame_count(self) -> int:
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

    @property
    def frame_count(self) -> int:
        return (
            next(
                self._cursor.execute(
                    """
            SELECT MAX(frame) FROM regions
            """
                )
            )[0]
            or 0
        )

    def frame_regions(self, frame: int) -> Iterator[Region]:
        for x1, y1, x2, y2, id_str, identity in self._cursor.execute(
            """
            SELECT x1, y1, x2, y2, id_str, identity FROM regions
            WHERE frame = ?
            """,
            (frame,),
        ):
            yield Region((x1, y1, x2, y2), id_str=id_str, identity=identity)


class CvatXmlRegionFile(RegionFile):
    def __init__(self, file_name: str) -> None:
        super().__init__()
        self._regions = self._get_regions_from_xml(file_name)

    def _load_xml(self, xml_path: str):
        xml_tree = ET.parse(xml_path)
        root = xml_tree.getroot()
        return root

    def _get_regions_from_xml(self, xml_path: str):
        """
        loads the specified XML and then calculates the regions of the boxes.
        """

        xml = self._load_xml(xml_path)
        # uses a dict for simplicity, can be converted into array if needed.
        # key is frame, value is list of centroids
        regions = []
        # iterate through each baboon
        for baboon in xml.iter("track"):
            identity = int(baboon.get("id"))

            # iterate through each labeled frame
            for box in baboon.iter("box"):
                frame = int(box.get("frame")) + 1

                xtl = floor(float(box.get("xtl")))
                ytl = floor(float(box.get("ytl")))
                xbr = ceil(float(box.get("xbr")))
                ybr = ceil(float(box.get("ybr")))

                region = (frame, identity, xtl, ytl, xbr, ybr)
                regions.append(region)

        regions.sort(key=lambda x: x[0])
        regions = np.array(regions, dtype=int)
        return regions

    def to_numpy(self):
        return self._regions

    @property
    def frame_count(self) -> int:
        if self._max_frame == 0:
            self._max_frame = max([f for f, _, _, _, _, _ in self._regions])

        return self._max_frame

    def frame_regions(self, frame: int) -> Iterator[Region]:
        return [
            Region((x1, y1, x2, y2), id_str=str(identity), identity=identity)
            for f, identity, x1, y1, x2, y2 in self._regions
            if f == frame
        ]


def region_factory(input_file: str) -> RegionFile:
    if basename(input_file) == "gt.txt":
        return GroundTruthTextRegionFile(input_file)
    elif splitext(input_file)[1] == ".xml":
        return CvatXmlRegionFile(input_file)
    elif splitext(input_file)[1] == ".db":
        return SqliteRegionFile(input_file)

    raise Exception("File type for region file not recognized.")
