"""
Implements a stage which shifts history frames.
"""
from typing import Deque, Dict, Tuple

import cv2
import numpy as np
from baboon_tracking.models.frame import Frame
from pipeline.stage import Stage


class ShiftHistoryFrames(Stage):
    """
    Implements a stage which shifts history frames.
    """

    def __init__(self, max_features: int, good_match_percent: float):
        Stage.__init__(self)

        self._orb = cv2.ORB_create(max_features)
        self._good_match_percent = good_match_percent
        self._feature_hash = dict()

    def _detect_and_compute(self, frame: Frame):
        if frame not in self._feature_hash:
            keypoints, descriptors = self._orb.detectAndCompute(frame.get_frame(), None)
            self._feature_hash[frame] = (keypoints, descriptors)

        return self._feature_hash[frame]

    def _register(self, frame1: Frame, frame2: Frame):
        keypoints1, descriptors1 = self._detect_and_compute(frame1)
        keypoints2, descriptors2 = self._detect_and_compute(frame2)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(
            cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        )
        matches = matcher.match(descriptors1, descriptors2, None)

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        num_good_matches = int(len(matches) * self._good_match_percent)
        matches = matches[:num_good_matches]

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # Find homography
        transformation_matrix, _ = cv2.findHomography(points1, points2, cv2.RANSAC)

        return transformation_matrix

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Registers the history frame.
        """
        previous_frame: Frame = state["gray"]
        history_frames: Deque[Frame] = state["history_frames"]

        transformation_matrices = [
            self._register(previous_frame, f) for f in history_frames
        ]

        state["shifted_history_frames"] = [
            Frame(
                cv2.warpPerspective(
                    previous_frame.get_frame(),
                    M,
                    (
                        previous_frame.get_frame().shape[1],
                        previous_frame.get_frame().shape[0],
                    ),
                ).astype(np.uint8),
                previous_frame.get_frame_number(),
            )
            for M in transformation_matrices
        ]

        return (True, state)
