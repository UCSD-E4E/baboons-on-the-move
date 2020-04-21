#!/usr/bin/python3
import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Find contours and centroids")
parser.add_argument('input', help='Source video')
parser.add_argument('-o', '--output', help='Output video', default='output.mp4')

args = parser.parse_args()

# video capture (reader)
cap = cv2.VideoCapture(args.input)
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('frame', 800, 600)

# video writer
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter(args.output, fourcc, fps, (w, h))

# kernels
erosion_kernel = np.ones((5, 5), np.uint8)
dilation_kernel = np.ones((5, 5), np.uint8)

# blob detection  ================================
# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()
# Change thresholds
params.minDistBetweenBlobs = 0
params.filterByColor = True
params.blobColor = 255
params.filterByArea = True
params.minArea = 10
params.maxArea = 300000
params.filterByCircularity = False
params.filterByConvexity = False
params.filterByInertia = True
params.minInertiaRatio = 0.01
params.maxInertiaRatio = 1
detector = cv2.SimpleBlobDetector_create(params)
# ================================================

while(cap.isOpened()):
    ret, frame = cap.read()

    if(frame is None):
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Delete this block when blobs are cohesive =========
    gray = cv2.erode(gray , erosion_kernel, iterations=1)
    gray = cv2.dilate(gray, dilation_kernel, iterations=1)
    # ===================================================

    # contour detection
    ret, thresh = cv2.threshold(gray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # blob detection
    keypoints = detector.detect(gray)
    
    frame = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    frame = cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    for c in contours:
        # compute the center of the contour
        M = cv2.moments(c)
        # if M[“m00”] is zero, neglects the contours which are not segmented properly
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        # draw the contour and center of the shape on the image
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (cX, cY), 2, (0, 0, 255), -1)
     
    cv2.imshow('frame', frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
