import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing

from collections import deque

from config import *

def remove_noise(foreground_mask):
    '''
    Uses OpenCV morphological transformations to make blobs more defined
    Returns a foreground mask with more defined blobs
    '''
    erosion_kernel = np.ones(EROSION_KERNEL, np.uint8)
    dilation_kernel = np.ones(DILATION_KERNEL, np.uint8)

    foreground_mask = cv2.erode(foreground_mask, erosion_kernel, iterations = EROSION_ITERATIONS)
    foreground_mask = cv2.dilate(foreground_mask, dilation_kernel, iterations = DILATION_ITERATIONS)

    return foreground_mask

def detect_blobs(foreground_mask, rgb_frame, orig_frame=None):

    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(BLOB_DET_PARAMS)

    # DETECT BLOBS

    #invert image (blob detection only works with white background)
    foreground_mask = cv2.bitwise_not(foreground_mask)

    # apply blur
    foreground_mask = cv2.blur(foreground_mask, BLUR_KERNEL)

    # detect
    keypoints = detector.detect(foreground_mask)

    print("keypoints: ", keypoints)

    # draw detected blobs
    frame_with_blobs = cv2.drawKeypoints(rgb_frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 #creating another image with the keypoints drawn onto the image that it is finding keypoints on
    mask_with_blobs = cv2.drawKeypoints(foreground_mask, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    orig_with_blobs = None
    if(orig_frame is not None):
        orig_with_blobs = cv2.drawKeypoints(orig_frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return frame_with_blobs, mask_with_blobs, orig_with_blobs
