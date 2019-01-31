# source backgroundsubtraction/cv/bin/activate
import numpy as np
import cv2 as cv
# Straight from the opencv tutorial page https://docs.opencv.org/master/db/d5c/tutorial_py_bg_subtraction.html#gsc.tab=0
def draw_keypoints(vis, keypoints, color = (0, 255, 255)):
    for kp in keypoints:
        x, y = kp.pt
        cv.circle(vis, (int(x), int(y)), 80, color)

params = cv.SimpleBlobDetector_Params()
params.minDistBetweenBlobs = 180
params.minArea = 30
params.maxArea = 100000000
params.minCircularity = 0
params.minConvexity = 0

cap = cv.VideoCapture('zoocam.avi')
fgbg = cv.bgsegm.createBackgroundSubtractorMOG()
# fgbg = cv.createBackgroundSubtractorMOG2(500, 16, True)
fourcc = cv.VideoWriter_fourcc('D', 'I', 'V', 'X')
out = cv.VideoWriter('output.avi', fourcc, 20, (int(cap.get(3)), int(cap.get(4))), False)
blobdetector = cv.SimpleBlobDetector_create(params)

while(1):
    ret, frame = cap.read()
    if ret == True:
        frame = cv.blur(frame, (3,3))
        fgmask = fgbg.apply(frame)
        # fgmask = fgbg.apply(frame, None, .04)
        inverted_img = cv.bitwise_not(fgmask)
        keypoints = blobdetector.detect(inverted_img)
        print keypoints
        draw_keypoints(frame, keypoints, (0,255,255))
        cv.imshow('frame',frame)
        out.write(fgmask)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
    else:
        break
cap.release()
out.release()
cv.destroyAllWindows()