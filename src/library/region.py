"""
Module for interacting with regions.
"""

from typing import Tuple
import numpy as np
import cv2


def get_region_mask(mask_size: Tuple[int, int], region: Tuple[int, int, int]):
    """
    Get a mask with the region made white.
    """
    frame_width, frame_height = mask_size

    mask = np.zeros((frame_height, frame_width, 3), np.uint8)

    x, y, radius = region
    x = int(x)
    y = int(y)
    radius = int(radius / 2)
    mask = cv2.circle(mask, (x, y), radius, (255, 255, 255), thickness=cv2.FILLED)

    return mask[:, :, 0].squeeze() == 255


def calculate_iou(region_1: Tuple[int, int, int], region_2: Tuple[int, int, int]):
    """
    Calculate the intersect over union
    """
    x_1, y_1, radius_1 = region_1
    x_2, y_2, radius_2 = region_2

    radius_1 = int(radius_1 / 2)
    radius_2 = int(radius_2 / 2)

    width = int(max(x_1 + radius_1, x_2 + radius_2))
    height = int(max(y_1 + radius_1, y_2 + radius_2))
    mask_size = (width + 10, height + 10)

    mask_1 = get_region_mask(mask_size, region_1)
    mask_2 = get_region_mask(mask_size, region_2)

    intersect = np.sum(np.logical_and(mask_1, mask_2).astype(np.float32))
    union = np.sum(np.logical_or(mask_1, mask_2).astype(np.float32))

    if intersect == 0:
        return 0

    return intersect / union


def check_if_same_region(
    region_1: Tuple[int, int, int], region_2: Tuple[int, int, int]
):
    """
    Tests to see if the two regions are similar enough to be considered the same.
    """
    return calculate_iou(region_1, region_2) > 0.2
