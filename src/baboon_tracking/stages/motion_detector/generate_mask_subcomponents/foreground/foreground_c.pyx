import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
cimport cython
cimport numpy as np
import  numpy as np
import time
import cv2
#from cython.parallel import prange
from baboon_tracking.mixins.foreground_mixin import ForegroundMixin
from baboon_tracking.mixins.intersected_frames_mixin import IntersectedFramesMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.mixins.unioned_frames_mixin import UnionedFramesMixin
from baboon_tracking.mixins.group_shifted_history_frames_mixin import GroupShiftedHistoryFramesMixin
from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from baboon_tracking.mixins.shifted_history_frames_mixin import ShiftedHistoryFramesMixin
from baboon_tracking.mixins.weights_mixin import WeightsMixin


@cython.boundscheck(False)
cdef zero_weights(np.ndarray[np.uint8_t, ndim=2] frame, np.ndarray[np.uint8_t, ndim=2] weights, int history_frames):
    cdef np.ndarray[np.uint8_t, ndim=2] f = frame.copy()
    cdef Py_ssize_t i,j
    cdef Py_ssize_t height = f.shape[0]
    cdef Py_ssize_t width = f.shape[1]
    cdef int hist_frames = history_frames - 1
    for i in range(height):
        for j in range(width):
            if(weights[i,j] >= hist_frames):
                f[i,j] = 0

    return f

cdef combine(np.ndarray[np.uint8_t, ndim=2] frame, np.ndarray[np.int32_t, ndim=2] q_frame1, np.ndarray[np.int32_t, ndim=2] q_frame2):
    """
    Combine function from the pipeline stage intersect_frames
    """
    mask = np.abs(q_frame1 - q_frame2) <= 1
    combined = frame.copy()
    combined[mask] = 0

    return combined
'''
cdef combine_loop(np.ndarray[np.uint8_t, ndim=2] frame, np.ndarray[np.int32_t, ndim=2] q_frame1, np.ndarray[np.int32_t, ndim=2] q_frame2):
    """
    Unpacking of combine function from intersect_frames as compiled loop
    """
    cdef np.ndarray[np.uint8_t, ndim=2] combined = frame.copy()
    cdef Py_ssize_t i,j
    cdef Py_ssize_t height = frame.shape[0]
    cdef Py_ssize_t width = frame.shape[1]
    cdef np.uint8_t diff
    for i in range(height):
        for j in range(width):
            diff = q_frame1[i,j]-q_frame2[i,j]
            if (diff <= 1 and diff >= -1):
                combined[i,j] = 0

    return combined

cpdef combine_par(np.ndarray[np.uint8_t, ndim=2] frame, np.ndarray[np.int32_t, ndim=2] q_frame1, np.ndarray[np.int32_t, ndim=2] q_frame2):
    
    cdef np.uint8_t[:,:] combined = frame
    cdef Py_ssize_t i,j
    cdef Py_ssize_t height = frame.shape[0]
    cdef Py_ssize_t width = frame.shape[1]
    cdef np.uint8_t diff
    for i in range(height):
        for j in range(width):
            diff = q_frame1[i,j]-q_frame2[i,j]
            if (diff <= 1 and diff >= -1):
                combined[i,j] = 0
    
    
    mask = np.abs(q_frame1 - q_frame2) <= 1
    combined = frame.copy()
    combined[mask] = 0

    return combined
'''
cdef group_and_intersect_frames(np.ndarray[np.uint8_t, ndim=3] shifted_history_frames, np.ndarray[np.int32_t, ndim=3] quantized_frames):
    """
    Groups and intersects frames as in stages group_frames and intersect_frames
    """
    cdef Py_ssize_t length = shifted_history_frames.shape[0]
    cdef Py_ssize_t i
    cdef np.ndarray[np.uint8_t, ndim=3] intersected_frames = np.zeros((length-1, shifted_history_frames.shape[1], shifted_history_frames.shape[2]), dtype=np.uint8)
    for i in range(length-1):
        intersected_frames[i] = (
            combine(shifted_history_frames[i],quantized_frames[i],quantized_frames[i+1])
            )
    return intersected_frames
'''
cdef group_and_intersect_frames_par(np.ndarray[np.uint8_t, ndim=3] shifted_history_frames, np.ndarray[np.int32_t, ndim=3] quantized_frames):
    """
    Groups and intersects frames as in stages group_frames and intersect_frames
    """
    cdef Py_ssize_t length = shifted_history_frames.shape[0]
    cdef Py_ssize_t i
    cdef np.uint8_t[:,:,:] shifted_history_frames_view = shifted_history_frames
    cdef np.int32_t[:,:,:] quantized_frames_view = quantized_frames
    cdef np.uint8_t[:,:,:] intersected_frames = np.zeros((length-1, shifted_history_frames.shape[1], shifted_history_frames.shape[2]), dtype=np.uint8)
    
    for i in prange(length-1, nogil=True):
        intersected_frames[i] = (
            combine_par(shifted_history_frames_view[i],quantized_frames_view[i],quantized_frames_view[(i+1)])
            )

    
    return intersected_frames
'''

@cython.boundscheck(False)
cdef union_frames(np.ndarray[np.uint8_t, ndim=3] frames):
    """
    Unpacking of the UnionFrames algorithm into a compiled loop
    """
    cdef np.ndarray[np.uint8_t, ndim=2] union = np.zeros(frames[0].shape, dtype=np.uint8)

    cdef Py_ssize_t i, j, k
    cdef Py_ssize_t frame_count = frames.shape[0]
    cdef Py_ssize_t height = frames.shape[1]
    cdef Py_ssize_t width = frames.shape[2]

    for i in range(frame_count-1, -1, -1):
        for j in range(height):
            for k in range(width):
                if (union[j,k] == 0):
                    union[j,k] = frames[i,j,k]
    
    return union

def subtract_background(np.ndarray[np.uint8_t, ndim=2] processed_frame, np.ndarray[np.uint8_t, ndim=2] unioned_frames, np.ndarray[np.uint8_t, ndim=2] weights, int history_frames):
    frame_new = zero_weights(processed_frame, weights, history_frames)
    union_new = zero_weights(unioned_frames, weights, history_frames)

    return cv2.absdiff(frame_new, union_new)
        

def foreground_all(shifted_history_frames, 
        quantized_frames,
        np.ndarray[np.uint8_t, ndim=2] processed_frame,
        np.ndarray[np.uint8_t, ndim=2] weights,
        int history_frames):
    #shifted_history_frames = np.stack([f.get_frame() for f in shifted_history_frames], axis=0)
    #quantized_frames = np.stack(quantized_frames, axis=0)
    intersected_frames = (group_and_intersect_frames_raw(shifted_history_frames,quantized_frames))
    unioned_frame = union_frames(intersected_frames)
    return subtract_background(processed_frame, unioned_frame, weights, history_frames)

def group_and_intersect_frames_raw(shifted_history_frames, quantized_frames):
    """
    Groups and intersects frames as in stages group_frames and intersect_frames
    """
    cdef Py_ssize_t length = len(shifted_history_frames)
    cdef Py_ssize_t i
    cdef np.ndarray[np.uint8_t, ndim=3] intersected_frames = np.zeros((length-1, shifted_history_frames[0].get_frame().shape[0], shifted_history_frames[0].get_frame().shape[1]), dtype=np.uint8)
    for i in range(length-1):
        intersected_frames[i] = (
            combine(shifted_history_frames[i].get_frame(),quantized_frames[i],quantized_frames[i+1])
            )
    return intersected_frames
