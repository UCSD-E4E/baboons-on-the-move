import os
import cv2
cwd = os.getcwd()

DATA_PATH = '../data'
OUTPUT_PATH = '../out'

# OPENCV DISPLAY DIMENSIONS
DISPLAY_WIDTH = 1600
DISPLAY_HEIGHT = 900

### FOR __init__.py ###
INPUT_VIDEO = os.path.join(DATA_PATH, 'DJI_0769.MP4')
OUTPUT_MASK = os.path.join(OUTPUT_PATH, 'output_mask.mp4')

HISTORY_FRAME_COUNT = 10

### FOR test_dilate.py ###
INPUT_MASK = os.path.join(DATA_PATH, 'outpy_blur2x2.mp4')
OUTPUT_MASK_BLOB_DETECTION = os.path.join(OUTPUT_PATH, 'output_blobs.mp4')

BLUR_KERNEL = (5, 5)

EROSION_KERNEL = (2, 2)
EROSION_ITERATIONS = 1

DILATION_KERNEL = (5, 5)
DILATION_ITERATIONS = 5

# params for blob detector
BLOB_DET_PARAMS = cv2.SimpleBlobDetector_Params()

BLOB_DET_PARAMS.minThreshold = 10
BLOB_DET_PARAMS.maxThreshold = 200
BLOB_DET_PARAMS.filterByArea = True
BLOB_DET_PARAMS.minArea = 1
