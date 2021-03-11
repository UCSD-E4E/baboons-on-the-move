import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
cimport cython
cimport numpy as np
import  numpy as np
from cython.parallel import prange

from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin


@cython.boundscheck(False)
cdef get_mask(np.ndarray[np.int32_t, ndim=2] q_frame1, np.ndarray[np.int32_t, ndim=2] q_frame2):
    cdef Py_ssize_t i, j
    cdef Py_ssize_t height = q_frame1.shape[0]
    cdef Py_ssize_t width = q_frame2.shape[1]
    cdef np.ndarray[np.uint8_t, ndim=2] mask = np.zeros((q_frame1.shape[0], q_frame1.shape[1]), dtype=np.uint8)
    cdef int diff
    for i in range(height):
        for j in range(width):
            diff = q_frame1[i,j]-q_frame2[i,j]
            if(diff <= 1 and diff >= -1):
                mask[i,j] = 1
    return mask

@cython.boundscheck(False)
cdef get_mask_par(np.int32_t[:,:] q_frame1, np.int32_t[:,:] q_frame2):
    cdef Py_ssize_t i, j
    cdef Py_ssize_t height = q_frame1.shape[0]
    cdef Py_ssize_t width = q_frame2.shape[1]
    cdef np.uint8_t[:,:] mask = np.zeros((q_frame1.shape[0], q_frame1.shape[1]), dtype=np.uint8)
    cdef np.int32_t diff
    for i in prange(height, nogil=True):
        for j in prange(width):
            diff = q_frame1[i,j]-q_frame2[i,j]
            if(diff <= 1 and diff >= -1):
                mask[i,j] = 1
    
    return np.asarray(mask)

@cython.boundscheck(False)
def get_weights(q_frames):
    cdef Py_ssize_t i
    cdef Py_ssize_t length = len(q_frames)
    cdef np.ndarray[np.uint8_t, ndim=2] weights = np.zeros(q_frames[0].shape, dtype=np.uint8)
    for i in range(length-1):
        weights = weights + get_mask_par(q_frames[i], q_frames[i+1])
    
    return weights