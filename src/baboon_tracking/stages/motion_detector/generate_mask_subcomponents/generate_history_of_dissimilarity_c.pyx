import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
cimport cython
cimport numpy as np
import  numpy as np

from cython.parallel import prange
from libc.stdlib cimport abs

from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from baboon_tracking.mixins.shifted_history_frames_mixin import (
    ShiftedHistoryFramesMixin,
)

@cython.boundscheck(False)
@cython.cdivision(True)
def get_history_of_dissimilarity(frames, q_frames):
    """
    Returns the history of dissimilarity as in _get_history_of_dissimilarity
    """
    cdef Py_ssize_t i, j, k
    cdef Py_ssize_t length = len(q_frames)
    cdef np.uint32_t[:,:] dissimilarity = np.zeros(q_frames[0].shape, dtype=np.uint32)
    cdef np.uint8_t[:,:] frame1, frame2
    cdef np.int32_t[:,:] q_frame1, q_frame2
    cdef Py_ssize_t height = q_frames[0].shape[0]
    cdef Py_ssize_t width = q_frames[0].shape[1]
    cdef np.int32_t diff
    cdef np.uint8_t frame_len = len(frames)
    # loop over the frames, then loop over each pixel in auto parallel, write to dissimilarity frame
    for i in range(length-1):
        frame1 = frames[i].get_frame()
        frame2 = frames[i+1].get_frame()
        q_frame1 = q_frames[i]
        q_frame2 = q_frames[i+1]
        for j in prange(height, nogil=True):
            for k in prange(width): 
                diff = abs(q_frame1[j,k]-q_frame2[j,k])
                if(diff <= 1):
                    dissimilarity[j,k] +=  abs(frame1[j,k]-frame2[j,k])


    

    cdef np.ndarray[np.uint32_t, ndim=2] dissim = np.asarray(dissimilarity)
    return (dissim/ len(frames)).astype(np.uint8)