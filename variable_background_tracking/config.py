import os
cwd = os.getcwd()

DATA_PATH = '../data'
# OPENCV DISPLAY DIMENSIONS
DISPLAY_WIDTH = 1600
DISPLAY_HEIGHT = 900

### FOR __init__.py ###
INPUT_VIDEO = os.path.join(DATA_PATH, 'DJI_0769.MP4')
OUTPUT_MASK = 'output_mask.mp4'

HISTORY_FRAME_COUNT = 10

### FOR test_dilate.py ###
INPUT_MASK = os.path.join(DATA_PATH, 'outpy_blur4x4.mp4')
OUTPUT_MASK_BLOB_DETECTION = 'output_blobs.mp4'
