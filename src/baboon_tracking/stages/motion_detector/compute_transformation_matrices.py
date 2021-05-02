"""
Compute the transformation matrices between the current frame and the historical frames.
"""
import cv2
import numpy as np
from baboon_tracking.mixins.history_frames_mixin import HistoryFramesMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from baboon_tracking.models.frame import Frame
from pipeline.decorators import config, stage
from pipeline.stage import Stage
from pipeline.stage_result import StageResult


@config(parameter_name="max_features", key="motion_detector/registration/max_features")
@config(
    parameter_name="good_match_percent",
    key="motion_detector/registration/good_match_percent",
)
@stage("preprocessed_frame")
@stage("history_frames")
class ComputeTransformationMatrices(Stage, TransformationMatricesMixin):
    """
    Compute the transformation matrices between the current frame and the historical frames.
    """

    def __init__(
        self,
        max_features: int,
        good_match_percent: float,
        preprocessed_frame: PreprocessedFrameMixin,
        history_frames: HistoryFramesMixin,
    ):
        TransformationMatricesMixin.__init__(self)
        Stage.__init__(self)

        self._orb = cv2.ORB_create(max_features)
        self._good_match_percent = good_match_percent
        self._feature_hash = dict()

        self._preprocessed_frame = preprocessed_frame
        self._history_frames = history_frames

        history_frames.history_frame_popped.subscribe(self._feature_hash.pop)

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

    def execute(self) -> StageResult:
        """
        Registers the history frame.
        """
        # Do nothing.
        if not self._history_frames.is_full():
            return StageResult(True, False)

        previous_frame = self._preprocessed_frame.processed_frame
        history_frames = self._history_frames.history_frames

        self.transformation_matrices = [
            self._register(previous_frame, f) for f in history_frames
        ]

        return StageResult(True, True)
