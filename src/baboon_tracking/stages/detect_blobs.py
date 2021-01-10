"""
Detect blobs using the built in OpenCV blob detector.
"""
from typing import Dict
import cv2
import numpy as np
from baboon_tracking.mixins.blob_image_mixin import BlobImageMixin
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.baboon import Baboon
from baboon_tracking.models.frame import Frame

from pipeline import Stage
from pipeline.decorators import config, stage
from pipeline.stage_result import StageResult


@config(parameter_name="blob_det_params", key="blob_detect/params")
@stage("moving_foreground")
class DetectBlobs(Stage, BlobImageMixin, BaboonsMixin):
    """
    Detect blobs using the built in OpenCV blob detector.
    """

    def __init__(
        self, blob_det_params: Dict[str, any], moving_foreground: MovingForegroundMixin,
    ) -> None:
        BlobImageMixin.__init__(self)
        BaboonsMixin.__init__(self)

        self._blob_det_params = cv2.SimpleBlobDetector_Params()
        for key in blob_det_params:
            setattr(self._blob_det_params, key, blob_det_params[key])

        self._moving_foregrouned = moving_foreground

        # Create a detector with the parameters
        self._detector = cv2.SimpleBlobDetector_create(self._blob_det_params)

        Stage.__init__(self)

    def execute(self) -> StageResult:
        """
        Detect and returns locations of blobs from foreground mask
        Returns list of coordinates
        """

        foreground_mask = self._moving_foregrouned.moving_foreground.get_frame()
        keypoints = self._detector.detect(foreground_mask)

        self.blob_image = Frame(
            cv2.drawKeypoints(
                cv2.cvtColor(foreground_mask, cv2.COLOR_GRAY2BGR),
                keypoints,
                np.array([]),
                (0, 255, 0),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            ),
            self._moving_foregrouned.moving_foreground.get_frame_number(),
        )

        self.baboons = [Baboon((k.pt[0], k.pt[1]), k.size) for k in keypoints]
        return StageResult(True, True)
