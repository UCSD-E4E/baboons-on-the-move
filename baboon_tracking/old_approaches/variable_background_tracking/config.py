import os
import cv2
cwd = os.getcwd()

DATA_PATH = '../data'
OUTPUT_PATH = './'

# OPENCV DISPLAY DIMENSIONS
DISPLAY_WIDTH = 1600
DISPLAY_HEIGHT = 900

### FOR __init__.py ###
#INPUT_VIDEO = os.path.join(DATA_PATH, 'DJI_0769.MP4')
INPUT_VIDEO = os.path.join(DATA_PATH, 'input.mp4')
OUTPUT_MASK = os.path.join(OUTPUT_PATH, 'output_mask.mp4')

HISTORY_FRAME_COUNT = 10

# 0 for new intersect, 1 for old (inefficient) intersect
ACTIVE_INTERSECT = 0

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
#adding a filter by inertia
BLOB_DET_PARAMS.filterByInertia = True
BLOB_DET_PARAMS.minInertiaRatio = 0.001


### DIFF VIDEOS
DIFF_VIDEO_1 = os.path.join(DATA_PATH, 'outpy_blur2x2.mp4')
DIFF_VIDEO_2 = os.path.join(DATA_PATH, 'output_mask_blur_2x2_new_intersect.mp4')
DIFF_OUTPUT = os.path.join(DATA_PATH, 'diff_output.mp4')

