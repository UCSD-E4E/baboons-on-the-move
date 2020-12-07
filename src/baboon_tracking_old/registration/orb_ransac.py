import cv2
import numpy as np
import math
import cmath

from .Registration import Registration
from ..models import Frame


class ORB_RANSAC_Registration(Registration):
    def __init__(self, history_frame_count, max_features, good_match_percent):
        super().__init__(history_frame_count, max_features, good_match_percent)

        self._orb = cv2.ORB_create(self.MAX_FEATURES)
        self._feature_hash = dict()

    def _detectAndCompute(self, frame: Frame):
        if frame not in self._feature_hash:
            keypoints, descriptors = self._orb.detectAndCompute(frame.get_frame(), None)
            self._feature_hash[frame] = (keypoints, descriptors)

        return self._feature_hash[frame]

    def push_history_frame(self, frame: Frame):
        """Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count, remove the oldest frame

        Args:
            frame: grayscale opencv image frame
        """
        popped_frame = super().push_history_frame(frame)

        if popped_frame is not None:
            del self._feature_hash[popped_frame]

        return popped_frame

    def register(self, frame1: Frame, frame2: Frame):
        """
        Registration function to find homography transformation between two frames using ORB
        Returns list of tuples containing (warped_frame, transformation matrix)
        (Not including most recent frame)
        """
        keypoints1, descriptors1 = self._detectAndCompute(frame1)
        keypoints2, descriptors2 = self._detectAndCompute(frame2)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(
            cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        )
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
