"""
Module for interacting with regions.
"""

from typing import Tuple


def bb_intersection_over_union(
    box_a: Tuple[int, int, int, int], box_b: Tuple[int, int, int, int]
):
    """
    Calculate the intersect over union
    """
    # determine the (x, y)-coordinates of the intersection rectangle
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])
    # compute the area of intersection rectangle
    inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
    box_b_area = (box_b[2] - box_b[0] + 1) * (box_b[3] - box_b[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = inter_area / float(box_a_area + box_b_area - inter_area)
    # return the intersection over union value
    return iou


def check_if_same_region(
    region_1: Tuple[int, int, int, int], region_2: Tuple[int, int, int, int]
):
    """
    Tests to see if the two regions are similar enough to be considered the same.
    """
    return bb_intersection_over_union(region_1, region_2) > 0.8
