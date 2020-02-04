import cv2
import numpy as np
import math
import cmath

from .Registration import Registration
from ..models import Frame

class ORB_RANSAC_Registration(Registration):
    def __init__(self, config):
        super().__init__(config)

        self._feature_hash = dict()

    def register(self, frame1: Frame, frame2: Frame):
        '''
        Registration function to find homography transformation between two frames using ORB
        Returns list of tuples containing (warped_frame, transformation matrix)
        (Not including most recent frame)
        '''
        orb = cv2.ORB_create(self.MAX_FEATURES)

        keypoints1, descriptors1 = orb.detectAndCompute(frame1.get_frame(), None)
        keypoints2, descriptors2 = orb.detectAndCompute(frame2.get_frame(), None)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        numGoodMatches = int(len(matches) * self.GOOD_MATCH_PERCENT)
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
