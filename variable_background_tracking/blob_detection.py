import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing

from collections import deque

def define_blobs(foreground_mask):
    '''
    Uses OpenCV morphological transformations to make blobs more defined
    Returns a foreground mask with more defined blobs
    '''
    kernel = np.ones((3,3),np.uint8)

    # open: erodes frame to eliminate noise, then re-dilate frame
    foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel)

    foreground_mask = cv2.dilate(foreground_mask ,kernel,iterations = 1)

    return foreground_mask

def detect_blobs():
    raise NotImplementedError
