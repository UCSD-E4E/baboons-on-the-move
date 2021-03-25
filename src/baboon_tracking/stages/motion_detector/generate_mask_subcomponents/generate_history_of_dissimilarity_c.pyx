import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
cimport cython
cimport numpy as np
import  numpy as np
import time

from cython.parallel import prange
from libc.stdlib cimport abs

from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from baboon_tracking.mixins.shifted_history_frames_mixin import (
    ShiftedHistoryFramesMixin,
)

@cython.boundscheck(False)
cdef get_dissimilarity_part_par(np.uint8_t[:,:] frame1, np.uint8_t[:,:] frame2, 
        np.int32_t[:,:] q_frame1, np.int32_t[:,:] q_frame2):
    cdef Py_ssize_t i, j
    cdef Py_ssize_t height = q_frame1.shape[0]
    cdef Py_ssize_t width = q_frame1.shape[1]
    cdef np.uint32_t[:,:] part = np.zeros((q_frame1.shape[0], q_frame1.shape[1]), dtype=np.uint32)
    cdef np.int32_t diff
    for i in prange(height, nogil=True):
        for j in prange(width):
            diff = abs(q_frame1[i,j]-q_frame2[i,j])
            if(diff <= 1):
                part[i,j] = abs(frame1[i,j]-frame2[i,j])
    
    return np.asarray(part)

@cython.boundscheck(False)
cdef get_dissimilarity_part_par2(np.uint32_t *dissimilarity, np.uint8_t[:,:] frame1, np.uint8_t[:,:] frame2, 
        np.int32_t[:,:] q_frame1, np.int32_t[:,:] q_frame2):
    cdef int i, j
    cdef Py_ssize_t height = q_frame1.shape[0]
    cdef Py_ssize_t width = q_frame1.shape[1]
    cdef np.int32_t diff
    for i in prange(height, nogil=True):
        for j in prange(width):
            diff = abs(q_frame1[i,j]-q_frame2[i,j])
            if(diff <= 1):
                dissimilarity[i*height+j] = abs(frame1[i,j]-frame2[i,j])

    return
'''
@cython.boundscheck(False)
def get_history_of_dissimilarity(frames, q_frames):
    cdef Py_ssize_t i
    cdef Py_ssize_t length = len(q_frames)
    #cdef np.ndarray[np.uint32_t, ndim=2] dissimilarity = np.zeros(q_frames[0].shape, dtype=np.uint32)
    cdef np.uint32_t[:,::1] dissimilarity = np.zeros(q_frames[0].shape, dtype=np.uint32)
    for i in range(length-1):
        t1 = time.time()
        get_dissimilarity_part_par2(&dissimilarity[0,0], frames[i].get_frame(), frames[i+1].get_frame(), 
                q_frames[i], q_frames[i+1])
        t2 = time.time()
        print('dissimilarity_call: ' + str((t2-t1)*1000))
    
        t1 = time.time()
        temp = get_dissimilarity_part_par(frames[i].get_frame(), frames[i+1].get_frame(), 
                q_frames[i], q_frames[i+1])
        t2 = time.time()
        print('part: ' + str((t2-t1)*1000))
        dissimilarity = dissimilarity + temp
        t3 = time.time()
        print('add: ' + str((t3-t2)*1000))
    
        
    cdef np.ndarray[np.uint32_t, ndim=2] dissim = np.asarray(dissimilarity)
    return (dissim/ len(frames)).astype(np.uint8)
'''



@cython.boundscheck(False)
@cython.cdivision(True)
def get_history_of_dissimilarity(frames, q_frames):
    cdef Py_ssize_t i, j, k
    cdef Py_ssize_t length = len(q_frames)
    #cdef np.ndarray[np.uint32_t, ndim=2] dissimilarity = np.zeros(q_frames[0].shape, dtype=np.uint32)
    cdef np.uint32_t[:,:] dissimilarity = np.zeros(q_frames[0].shape, dtype=np.uint32)
    cdef np.uint8_t[:,:] frame1, frame2
    cdef np.int32_t[:,:] q_frame1, q_frame2
    cdef Py_ssize_t height = q_frames[0].shape[0]
    cdef Py_ssize_t width = q_frames[0].shape[1]
    cdef np.int32_t diff
    cdef np.uint8_t frame_len = len(frames)
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