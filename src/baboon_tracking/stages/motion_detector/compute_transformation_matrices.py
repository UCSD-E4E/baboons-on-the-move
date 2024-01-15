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
from bom_pipeline.decorators import config, stage
from bom_pipeline.stage import Stage
from bom_pipeline.stage_result import StageResult
from third_party.ssc import ssc


@config(
    parameter_name="good_match_percent",
    key="motion_detector/registration/good_match_percent",
)
@config(
    parameter_name="ransac_max_error",
    key="motion_detector/registration/ransac_max_error",
)
@config(
    parameter_name="ssc_num_ret_points",
    key="motion_detector/registration/ssc_num_ret_points",
)
@config(
    parameter_name="ssc_tolerence",
    key="motion_detector/registration/ssc_tolerence",
)
@stage("preprocessed_frame")
@stage("history_frames")
class ComputeTransformationMatrices(Stage, TransformationMatricesMixin):
    """
    Compute the transformation matrices between the current frame and the historical frames.
    """

    def __init__(
        self,
        good_match_percent: float,
        ransac_max_error: float,
        ssc_num_ret_points: int,
        ssc_tolerence: float,
        preprocessed_frame: PreprocessedFrameMixin,
        history_frames: HistoryFramesMixin,
    ):
        TransformationMatricesMixin.__init__(self)
        Stage.__init__(self)

        self._orb = cv2.ORB_create()
        self._fast = cv2.FastFeatureDetector_create()
        self._good_match_percent = good_match_percent
        self._feature_hash = {}
        self._ransac_max_error = ransac_max_error
        self._ssc_num_ret_points = ssc_num_ret_points
        self._ssc_tolerence = ssc_tolerence

        self._preprocessed_frame = preprocessed_frame
        self._history_frames = history_frames

        history_frames.history_frame_popped.subscribe(self._feature_hash.pop)

    def _detect_and_compute(self, frame: Frame):
        if frame not in self._feature_hash:
            keypoints = self._fast.detect(frame.get_frame(), None)
            keypoints = ssc(
                keypoints,
                10000,
                0.1,
                frame.get_frame().shape[1],
                frame.get_frame().shape[0],
            )
            descriptors = self._orb.compute(frame.get_frame(), keypoints)

            keypoints = descriptors[0]
            descriptors = descriptors[1]

            self._feature_hash[frame] = (keypoints, descriptors)

        return self._feature_hash[frame]

    def _register(self, frame1: Frame, frame2: Frame):
        keypoints1, descriptors1 = self._detect_and_compute(frame1)
        keypoints2, descriptors2 = self._detect_and_compute(frame2)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(
            cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        )
        matches = list(matcher.match(descriptors1, descriptors2, None))

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
        transformation_matrix, _ = cv2.findHomography(
            points1, points2, cv2.RANSAC, self._ransac_max_error
        )

        return transformation_matrix

    def execute(self) -> StageResult:
        """
        Registers the history frame.
        """
        # Do nothing.
        if not self._history_frames.is_full():
            return StageResult(True, False)

        processed_frame = self._preprocessed_frame.processed_frame
        history_frames = self._history_frames.history_frames

        self.transformation_matrices = [
            self._register(f, processed_frame) for f in history_frames
        ]
        self.current_frame_transformation = self._register(
            processed_frame, history_frames[-1]
        )

        return StageResult(True, True)
