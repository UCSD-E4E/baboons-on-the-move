"""
A collection of helper methods.
"""

import math
from typing import List

import numpy as np

from baboon_tracking.models.frame import Frame


def flatten(collection: List[any]):
    """
    Flattens a list of lists into a single list.
    """
    return [item for sublist in collection for item in sublist]


def scale_ndarray(array: np.ndarray, frame_number: int) -> Frame:
    max_value = float(np.max(array))
    if max_value > 0:
        scale_factor = np.array([math.floor(255.0 / max_value)], dtype=np.uint8)
    else:
        scale_factor = np.array([1], dtype=np.uint8)

    scaled_array = scale_factor * array
    return Frame(scaled_array, frame_number)
