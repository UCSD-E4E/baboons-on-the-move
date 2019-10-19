# Usage: python old_tracking.py path_to_bit_mask path_to_video
import numpy as np
import cv2 as cv
import math
import sys

font = cv.FONT_HERSHEY_SIMPLEX
blur_radius = 15
params = cv.SimpleBlobDetector_Params()
params.minDistBetweenBlobs = 14
params.minArea = 5
params.maxArea = 100000000
params.minCircularity = 0
params.minConvexity = 0
distthresh = 80
momentum_ratio = .5
min_age = 15
history = 16
circle_radius = 80
bgsub_history = 300
nmixtures = 10
background_ratio = .7
video_fps = 30
fourcc = cv.VideoWriter_fourcc('D', 'I', 'V', 'X')
kpthresh = 60

BGSUB_MODE = 0
OPTICAL_FLOW_MODE = 1
state = BGSUB_MODE
MAX_BLOBS_DIFF = 3 # Max difference in blobs from frame to frame
MAX_BLOBS = 50 # Max difference in blobs total

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

# Straight from the opencv tutorial page
# https://docs.opencv.org/master/db/d5c/tutorial_py_bg_subtraction.html#gsc.tab=0
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

cap = cv.VideoCapture(sys.argv[1])
discap = cv.VideoCapture(sys.argv[2])
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
                first = avgkeypoints(self.keypoints[0:int(length/2)], True)
                last = avgkeypoints(self.keypoints[int(length/2):length], True)
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

# ret, old_frame = cap.read()
# old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)
# track = cv.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

last_size = -1
while(1):
    ret, frame = cap.read()
    retdis, framedis = discap.read()
    if ret == True:
        # Blob detection to see viability of background subtraction
        fgmask = fgbg.apply(frame, .1)
        # fgmask = fgbg.apply(frame, None, .04)
        inverted_img = cv.bitwise_not(frame)
        # inverted_img = cv.medianBlur(inverted_img, 3)
        keypoints = blobdetector.detect(inverted_img)

        # Get grayscale image
        new_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        print(len(keypoints))
        if len(keypoints) > kpthresh:
            continue

        # Check for state
        # if last_size == -1 or len(keypoints) <= MAX_BLOBS:
            # state = BGSUB_MODE
            # last_size = len(keypoints)
            # cv.putText(frame, 'BGSUB_MODE', (10, 200), font, 5, (0, 255, 255), 2,
                    # cv.LINE_AA)
        # else:
            # state = OPTICAL_FLOW_MODE
            # cv.putText(frame, 'OPTICAL_FLOW_MODE', (10, 200), font, 5, (0, 255, 255), 2,
                    # cv.LINE_AA)

        # Update keypoint trackers
        for tracker in keypointtrackers:
            tracker.update()
            tracker.updated = False
            if tracker.updateswithout > 60:
                keypointtrackers.remove(tracker)

        if state == BGSUB_MODE:
            for kp in keypoints:
                oldkp = False
                added = False
                for tracker in keypointtrackers:
                    dis = distance(kp.pt, tracker.latest().pt)
                    if dis < distthresh:
                        tracker.add(kp)
                        added = True
                if not added:
                    newkpt = KeypointTracker(kp)
                    keypointtrackers.append(newkpt)
            draw_keypoints(framedis, keypointtrackers, (0,255,255))

        # if state == OPTICAL_FLOW_MODE:
            # fgbg = cv.bgsegm.createBackgroundSubtractorMOG(bgsub_history, nmixtures, background_ratio)
            # state = BGSUB_MODE

            # tracked = np.zeros((1, len(keypointtrackers), 2), np.float32)
            # for i in range(len(keypointtrackers)):
                # tracked[0][i][0] = keypointtrackers[i].keypoints[0].pt[0]
                # tracked[0][i][1] = keypointtrackers[i].keypoints[0].pt[1]

            # newpoints, st, err = cv.calcOpticalFlowPyrLK(old_gray, new_gray,
                # tracked, None, **lk_params)

            # if newpoints is not None and st is not None:

                # # updating keypoints with tracked points
                # for point in newpoints[0]:
                    # x, y = point.ravel()
                    # newkp = cv.KeyPoint(x, y, 5)

                    # added = False
                    # for tracker in keypointtrackers:
                        # dis = distance(newkp.pt, tracker.latest().pt)
                        # if dis < distthresh:
                            # tracker.add(newkp)
                            # added = True
                    # if not added:
                        # newkpt = KeypointTracker(newkp)
                        # keypointtrackers.append(newkpt)
            # draw_keypoints(frame, keypointtrackers, (0,255,255))

        # old_frame = new_gray

        out.write(framedis)

# Resize for showing
        frame = cv.resize(framedis, (int(cap.get(3)/2.3), int(cap.get(4)/2.3)), interpolation = cv.INTER_AREA)

        # print("frame")
        cv.imshow("Frame", framedis)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
    else:
        break
cap.release()
out.release()
cv.destroyAllWindows()

