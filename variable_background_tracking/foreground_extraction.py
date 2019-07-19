import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing

from collections import deque
from registration import register

from config import *

history_frames = deque([])
def push_history_frame(frame):
    '''
    Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count,
    remove the oldest frame
    '''
    if len(history_frames) == HISTORY_FRAME_COUNT:
        history_frames.popleft()

    history_frames.append(frame)

def shift_frame(input):
    '''
    Takes in transformation matrix; does homography transformation to register/align two frames
    '''
    frame = input[0]
    previous_frame = input[1]

    M = register(previous_frame, frame)

    return (cv2.warpPerspective(previous_frame, M, (previous_frame.shape[1], previous_frame.shape[0])).astype(np.uint8), M)

def quantize(frame):
    '''
    Normalize pixel values from 0-255 to values from 0-10
    Returns quantized frame
    '''
    return (frame.astype(np.float32) * 10 / 255).astype(np.int8)

def intersect_frames(frames, q_frames):
    '''
    Intersect two consecutive frames to find common background between those two frames
    Returns the single frame produced by intersection
    '''
    print('intersect')

    mask = np.abs(q_frames[0] - q_frames[1]) <= 1
    combined = frames[0]
    combined[mask] = 0

    return combined

def intersect_frames_old(frames, q_frames):
    '''
    Intersect two consecutive frames to find common background between those two frames
    Returns the single frame produced by intersection
    '''
    print('intersect_old')

    mask = (np.abs(q_frames[0] - q_frames[1]) <= 1).astype(np.float64)
    combined = (np.multiply(skimage.img_as_float(frames[0]), mask) + np.multiply(skimage.img_as_float(frames[1]), mask)) / 2.0

    return skimage.img_as_ubyte(combined)


def union_frames(frames):
    '''
    Union all frame intersections to produce acting background for all frames
    Returns the single union frame produced by unioning all frames in input
    '''
    print('union')

    union = np.zeros(frames[0].shape).astype(np.uint8)

    for f in frames:
        union[union == 0] = f[union == 0]

    return union

def get_history_of_dissimilarity(frames, q_frames):
    '''
    Calculate history of dissimilarity according to figure 10 of paper
    Returns frame representing history of dissimilarity
    '''
    print('dissimilarity')

    dissimilarity = np.zeros(frames[0].shape).astype(np.uint32)

    for i in range(len(frames)):
        if i == 0:
            continue

        mask = (np.abs(q_frames[i] - q_frames[i - 1]) > 1).astype(np.uint32)
        dissimilarity = dissimilarity + np.multiply(np.abs(frames[i].astype(np.int32) - frames[i - 1].astype(np.int32)), mask)

    return (dissimilarity / len(frames)).astype(np.uint8)

def get_weights(q_frames):
    '''
    Calculate weights based on frequency of commonality between frames according
    to figure 12 of paper
    Returns frame representing frequency of commonality
    '''
    print('weights')

    weights = np.zeros(q_frames[0].shape).astype(np.uint8)

    for i, q in enumerate(q_frames):
        if i == 0:
            continue

        mask = (np.abs(q_frames[i] - q_frames[i - 1]) <= 1).astype(np.uint8)
        weights = weights + mask

    return weights

def zero_weights(frame, weights):
    '''
    Gets foreground of frame by zeroing out all pixels with large weights, i.e. pixels in which frequency of commonality
    is really high, meaning that it hasn't changed much or at all in the history frames, according to figure 13 of paper
    Returns frame representing the foreground
    '''
    print('zero')

    f = frame.copy()
    f[weights >= HISTORY_FRAME_COUNT - 1] = 0

    return f

def get_moving_foreground(weights, foreground, dissimilarity):
    '''
    Calculates moving foreground according to figure 14 of paper
    Each of W and D (weights and dissimilarity) is assigned to high, medium, and low

    Medium commonality AND low commonality but low dissimiliarity are considered moving foreground
    Otherwise, it is either a still or flickering background

    Return frame representing moving foreground
    '''
    history_frame_count_third = math.floor(float(HISTORY_FRAME_COUNT - 1) / 3)
    third_gray = 255.0 / 3.0

    weights_low = (weights <= history_frame_count_third).astype(np.uint8)
    weights_medium = np.logical_and(history_frame_count_third < weights, weights < HISTORY_FRAME_COUNT - 1).astype(np.uint8) * 2

    weight_levels = weights_low + weights_medium

    foreground_low = (foreground <= math.floor(third_gray)).astype(np.uint8)
    foreground_medium = ((math.floor(third_gray) < foreground) + (foreground < math.floor(2 * third_gray))).astype(np.uint8) * 2
    foreground_high = (foreground >= math.floor(2 * third_gray)).astype(np.uint8) * 3

    foreground_levels = foreground_low + foreground_medium + foreground_high

    dissimilarity_low = (dissimilarity <= math.floor(third_gray)).astype(np.uint8)
    dissimilarity_medium = ((math.floor(third_gray) < dissimilarity) + (dissimilarity < math.floor(2 * third_gray))).astype(np.uint8) * 2
    dissimilarity_high = (dissimilarity >= math.floor(2 * third_gray)).astype(np.uint8) * 3

    dissimilarity_levels = dissimilarity_low + dissimilarity_medium + dissimilarity_high

    moving_foreground = np.logical_and(weight_levels == 2, np.greater_equal(foreground_levels, dissimilarity_levels)).astype(np.uint8)
    moving_foreground = moving_foreground + np.logical_and(weight_levels == 1, np.logical_and(dissimilarity_levels == 1, np.greater(foreground_levels, dissimilarity_levels))).astype(np.uint8)

    return moving_foreground * 255

