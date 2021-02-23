import numpy as np
import cv2
from baboon_tracking.mixins.foreground_mixin import ForegroundMixin
from baboon_tracking.mixins.intersected_frames_mixin import IntersectedFramesMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.mixins.unioned_frames_mixin import UnionedFramesMixin
from baboon_tracking.mixins.group_shifted_history_frames_mixin import GroupShiftedHistoryFramesMixin
from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from baboon_tracking.mixins.shifted_history_frames_mixin import ShiftedHistoryFramesMixin
from baboon_tracking.mixins.weights_mixin import WeightsMixin

'''
def combine(frames, q_frames):
    mask = np.abs(q_frames[0] - q_frames[1]) <= 1
    combined = frames[0].get_frame().copy()
    combined[mask] = 0

    return combined

def group_history(shifted_history_frames):
    frame_group_index = range(len(shifted_history_frames) - 1)
    frame_group_index = [(r, r + 1) for r in frame_group_index]

    grouped_shifted_history_frames = [
        (shifted_history_frames[g[0]], shifted_history_frames[g[1]])
        for g in frame_group_index
    ]

    return grouped_shifted_history_frames

def group_quantized(quantized_frames):
    frame_group_index = range(len(quantized_frames) - 1)
    frame_group_index = [(r, r + 1) for r in frame_group_index]

    grouped_quantized_frames = [
        (quantized_frames[g[0]], quantized_frames[g[1]]) for g in frame_group_index
    ]

    return grouped_quantized_frames

def group_frames(shifted_history_frames, quantized_frames):
    frame_group_index = range(len(shifted_history_frames) - 1)
    frame_group_index = [(r, r + 1) for r in frame_group_index]

    grouped_shifted_history_frames = [
        (shifted_history_frames[g[0]], shifted_history_frames[g[1]])
        for g in frame_group_index
    ]
    grouped_quantized_frames = [
        (quantized_frames[g[0]], quantized_frames[g[1]]) for g in frame_group_index
    ]

    return grouped_shifted_history_frames, grouped_quantized_frames

def intersect_frames(grouped_shifted_history_frames, grouped_quantized_frames):
    intersected_frames = [
        combine(z[0], z[1])
        for z in zip(grouped_shifted_history_frames, grouped_quantized_frames)
    ]

    return intersected_frames
'''

def zero_weights(frame, weights, history_frames):
    f = frame.copy()
    f[weights >= history_frames - 1] = 0

    return f


def combine(frame, q_frame1,q_frame2):
    """
    Combine function from the pipeline stage intersect_frames
    """
    mask = np.abs(q_frame1 - q_frame2) <= 1
    combined = frame.get_frame().copy()
    combined[mask] = 0

    return combined

def group_and_intersect_frames(shifted_history_frames, quantized_frames):
    """
    Groups and intersects frames as in stages group_frames and intersect_frames
    """
    intersected_frames = []
    for i in range(len(shifted_history_frames)-1):
        intersected_frames.append(
            combine(shifted_history_frames[i],quantized_frames[i],quantized_frames[i+1])
            )
    return intersected_frames

def union_frames(frames: IntersectedFramesMixin):
    """
    Unions frames using same methods as in union_intersections stage
    """
    union = np.zeros(frames[0].shape, dtype=np.uint8)
    f_copy = frames.copy()
    f_copy.reverse()
    for f in f_copy:
        union[union == 0] = f[union == 0]

    return union

def subtract_background(processed_frame, unioned_frames, weights, history_frames):

    frame_new = zero_weights(processed_frame.get_frame(), weights, history_frames)
    union_new = zero_weights(unioned_frames, weights, history_frames)

    return cv2.absdiff(frame_new, union_new)
        

