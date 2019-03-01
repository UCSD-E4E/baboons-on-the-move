import numpy as np
import cv2 as cv
import math
import sys

bgsub_history = 300
nmixtures = 10
background_ratio = .7
# Video reading params
video_fps = 20
fourcc = cv.VideoWriter_fourcc('D', 'I', 'V', 'X')
# Blob detector params
params = cv.SimpleBlobDetector_Params()
params.minDistBetweenBlobs = 5 
params.minArea = 20
params.maxArea = 100000000
params.minCircularity = 0
params.minConvexity = 0

cap = cv.VideoCapture('zoocam3.avi')
fgbg = cv.bgsegm.createBackgroundSubtractorMOG(bgsub_history, nmixtures, background_ratio)
# fgbg = cv.createBackgroundSubtractorMOG2(500, 16, True)
out = cv.VideoWriter('output.avi', fourcc, video_fps, (int(cap.get(3)), int(cap.get(4))), True)

blobdetector = cv.SimpleBlobDetector_create(params)
while(1):
    ret, frame = cap.read()
    if ret == True:
        # Edge detection
        edges = cv.Canny(frame,100,200)
        cv.imshow('frame', edges)
        out.write(edges)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
    else: 
      break

cap.release()
out.release()
cv.destroyAllWindows()