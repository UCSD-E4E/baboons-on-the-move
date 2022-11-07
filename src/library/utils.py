import numpy as np
import math

from baboon_tracking.models.frame import Frame


def scale_ndarray(array: np.ndarray, frame_number: int) -> Frame:
    max_value = float(np.max(array))
    scale_factor = np.array([math.floor(255.0 / max_value)]).astype(np.uint8)

    scaled_array = scale_factor * array
    return Frame(scaled_array, frame_number)
