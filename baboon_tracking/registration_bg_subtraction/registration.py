import cv2
import numpy as np
from collections import deque

MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15

history_frame_count = 4

history_frames = deque([])
history_frames_gray = deque([])
def push_history_frame(frame, grayframe):
    '''
    Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count,
    remove the oldest frame
    '''
    if len(history_frames) == history_frame_count:
        history_frames.popleft()

    history_frames.append(frame)

    if len(history_frames_gray) == history_frame_count:
        history_frames_gray.popleft()

    history_frames_gray.append(grayframe)

def register(frame1, frame2):
    '''
    Registration function to find homography transformation between two frames using ORB
    Returns transformation matrix to convert frame1 to frame2
    '''
    orb = cv2.ORB_create(MAX_FEATURES)

    keypoints1, descriptors1 = orb.detectAndCompute(frame1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(frame2, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove not so good matches
    numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
    matches = matches[:numGoodMatches]

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    return h

def shift_frame(input):
    '''
    Takes in transformation matrix; does homography transformation to register/align two frames
    '''
    frame = input[0]
    previous_frame = input[1][0]
    previous_frame_color = input[1][1]

    M = register(previous_frame, frame)

    return (cv2.warpPerspective(previous_frame_color, M, (previous_frame.shape[1], previous_frame.shape[0])).astype(np.uint8), M)

