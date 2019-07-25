import numpy as np
import cv2 as cv
# Straight from the opencv tutorial page https://docs.opencv.org/master/db/d5c/tutorial_py_bg_subtraction.html#gsc.tab=0
cap = cv.VideoCapture('zoocam.avi')
fgbg = cv.createBackgroundSubtractorMOG2(500, 16, True)
fourcc = cv.VideoWriter_fourcc('D', 'I', 'V', 'X')
out = cv.VideoWriter('output.avi', fourcc, 20, (int(cap.get(3)), int(cap.get(4))), False)
while(1):
    ret, frame = cap.read()
    if ret == True:
        frame = cv.blur(frame, (3,3))
        fgmask = fgbg.apply(frame, None, .04)
        cv.imshow('frame',fgmask)
        out.write(fgmask)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
    else:
        break
cap.release()
out.release()
cv.destroyAllWindows()