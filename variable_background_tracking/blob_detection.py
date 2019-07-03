import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing

from collections import deque

def remove_noise(foreground_mask):
    '''
    Uses OpenCV morphological transformations to make blobs more defined
    Returns a foreground mask with more defined blobs
    '''
    kernel1 = np.ones((2,2),np.uint8)
    kernel2 = np.ones((5,5),np.uint8)

    foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel1)
    #foreground_mask = cv2.erode(foreground_mask ,kernel,iterations = 1)
    foreground_mask = cv2.dilate(foreground_mask ,kernel2,iterations = 5)

    return foreground_mask

def detect_blobs(foreground_mask, rgb_frame):

    # SETTINGS

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 1

    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)

    # DETECT BLOBS

    #invert image (blob detection only works with white background)
    foreground_mask = cv2.bitwise_not(foreground_mask)

    # apply blur
    foreground_mask = cv2.blur(foreground_mask, (5, 5))

    # detect
    keypoints = detector.detect(foreground_mask)

    print("keypoints: ", keypoints)

    # draw detected blobs
    frame_with_blobs = cv2.drawKeypoints(rgb_frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return frame_with_blobs
