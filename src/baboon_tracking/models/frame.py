import numpy as np


class Frame:
    __slots__ = ["_frame", "_frame_number"]

    def __init__(self, frame: np.array, frame_number: int):
        self._frame = frame
        self._frame_number = frame_number

    def get_frame(self) -> np.array:
        return self._frame

    def get_frame_number(self) -> int:
        return self._frame_number

    def __hash__(self):
        return self.get_frame_number()
