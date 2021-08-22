"""
Represents a frame from a video file.
"""
import numpy as np


class Frame:
    """
    Represents a frame from a video file.
    """

    def __init__(self, frame: np.array, frame_number: int):
        self._frame = frame
        self._frame_number = frame_number

    def get_frame(self) -> np.array:
        """
        Gets the frame image.
        """

        return self._frame

    def get_frame_number(self) -> int:
        """
        Gets the frame index.
        """

        return self._frame_number

    def set_frame(self, frame: np.array):
        """
        Sets the frame image.
        """

        self._frame = frame

    def __hash__(self):
        return self.get_frame_number()
