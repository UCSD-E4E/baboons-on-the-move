# source backgroundsubtraction/cv/bin/activate
# TODO: Make const file
# TODO: Add velocity arrows
# TODO: Brighten dark areas
import numpy as np
import cv2 as cv
import math
import sys

blur_radius = 15
params = cv.SimpleBlobDetector_Params()
params.minDistBetweenBlobs = 5 
params.minArea = 20
params.maxArea = 100000000
params.minCircularity = 0
params.minConvexity = 0
distthresh = 100
momentum_ratio = .5
min_age = 15
history = 16
circle_radius = 80
bgsub_history = 300
nmixtures = 10
background_ratio = .7
video_fps = 20
fourcc = cv.VideoWriter_fourcc('D', 'I', 'V', 'X')

# Straight from the opencv tutorial page https://docs.opencv.org/master/db/d5c/tutorial_py_bg_subtraction.html#gsc.tab=0
def draw_keypoints(vis, keypoints, color = (0, 255, 255)):
    for kp in keypoints:
        if kp.age > min_age:
            x, y = kp.latest().pt
            dx, dy = kp.velocity
            cv.circle(vis, (int(x), int(y)), circle_radius, color)
            cv.circle(vis, (int(x), int(y)), 1, color, 2)
            cv.line(vis, (int(x), int(y)), (int(x) + int(dx), int(y) + int(dy)), color, 2)

def dkp(vis, keypoints, color = (0, 255, 255)):
    for kp in keypoints:
        x, y = kp.pt
        cv.circle(vis, (int(x), int(y)), 10, color)

cap = cv.VideoCapture('zoocam.avi')
fgbg = cv.bgsegm.createBackgroundSubtractorMOG(bgsub_history, nmixtures, background_ratio)
# fgbg = cv.createBackgroundSubtractorMOG2(500, 16, True)
out = cv.VideoWriter('output.avi', fourcc, video_fps, (int(cap.get(3)), int(cap.get(4))), True)
blobdetector = cv.SimpleBlobDetector_create(params)
keypointtrackers = []

# Keeps track of active keypoints
class KeypointTracker:
    def __init__(self, keypoint):
        self.keypoints = []
        self.cycleavg = []
        self.keypoints.append(keypoint)
        self.updateswithout = 0
        self.age = 0
        self.updated = False
        self.velocity = (0,0)
    
    def add(self, keypoint = None):
        if not keypoint == None:
            self.cycleavg.append(keypoint)
        self.updated = True

    def update(self):
        self.age += 1
        if self.updated == False:
            self.updateswithout += 1
        else:
            key = avgkeypoints(self.cycleavg)
            length = len(self.keypoints)
            if length >= history:
                first = avgkeypoints(self.keypoints[0:length/2], True)
                last = avgkeypoints(self.keypoints[length/2:length], True)
                self.velocity = (last.pt[0] - first.pt[0], last.pt[1] - first.pt[1])
                expected_position = avgkeypoints(self.keypoints, True)

                pt = expected_position.pt
                expected_position.pt = (pt[0] + self.velocity[0], pt[1] + self.velocity[1])
                key.pt = (key.pt[0]*(1-momentum_ratio) + expected_position.pt[0]*momentum_ratio, key.pt[1]*(1-momentum_ratio) + expected_position.pt[1]*momentum_ratio)
            self.keypoints.append(key)
            if length > history:
                del self.keypoints[0]
            self.cycleavg = []
            self.updateswithout = 0
    
    def latest(self):
        return self.keypoints[len(self.keypoints) - 1]

def avgkeypoints(keypoints, ignoreweight = False):
    weight = 0
    total = (0.0, 0.0)
    for kp in keypoints:
        if ignoreweight: 
            total = (total[0] + kp.pt[0], total[1] + kp.pt[1])
            weight += 1
        else: 
            total = (total[0] + kp.pt[0] * kp.size, total[1] + kp.pt[1] * kp.size)
            weight += kp.size
    if not weight == 0:
        total = (total[0]/weight,total[1]/weight)
    return cv.KeyPoint(total[0], total[1], 0)

def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

while(1):
    ret, frame = cap.read()
    if ret == True:
        brightened = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        brightened = cv.equalizeHist(brightened)
        fgmask = fgbg.apply(brightened, .1)
        # fgmask = fgbg.apply(frame, None, .04)
        inverted_img = cv.bitwise_not(fgmask)
        inverted_img = cv.blur(inverted_img, (blur_radius,blur_radius))
        # inverted_img = cv.blur(inverted_img, (blur_radius,blur_radius))
        # reti, inverted_img = cv.threshold(inverted_img, 240, 255, cv.THRESH_BINARY)
        keypoints = blobdetector.detect(inverted_img)

        for tracker in keypointtrackers:
            tracker.update()
            tracker.updated = False
            if tracker.updateswithout > 5: 
                keypointtrackers.remove(tracker)

        for kp in keypoints:
            oldkp = False
            minimum = sys.maxsize
            besttracker = None
            for tracker in keypointtrackers:
                dis = distance(kp.pt, tracker.latest().pt)
                if minimum > dis:
                    minimum = dis
                    besttracker = tracker
            if minimum < distthresh:
                besttracker.add(kp)
            else:
                newkpt = KeypointTracker(kp)
                keypointtrackers.append(newkpt)

        draw_keypoints(frame, keypointtrackers, (0,255,255))
        dkp(frame, keypoints, (0, 255, 255))
        cv.imshow('frame',frame)
        out.write(frame)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
    else:
        break
cap.release()
out.release()
cv.destroyAllWindows()

