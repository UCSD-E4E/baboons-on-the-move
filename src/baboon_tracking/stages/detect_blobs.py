from typing import Tuple
import cv2
import numpy as np
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin

from pipeline import Stage
from pipeline.decorators import config, stage
from pipeline.stage_result import StageResult


@config(parameter_name="blob_det_params", key="blob_det_params")
@config(parameter_name="blur_kernel", key="blur_kernel")
@config(parameter_name="erosion_kernel", key="erosion_kernel")
@config(parameter_name="erosion_iterations", key="erosion_iterations")
@config(parameter_name="dilation_kernel", key="dilation_kernel")
@config(parameter_name="dilation_iterations", key="dilation_iterations")
@stage("moving_foreground")
class DetectBlobs(Stage):
    def __init__(
        self,
        blob_det_params: float,
        blur_kernel: Tuple[float],
        erosion_kernel: Tuple[float],
        erosion_iterations: Tuple[float],
        dilation_kernel: Tuple[float],
        dilation_iterations: Tuple[float],
        moving_foreground: MovingForegroundMixin,
    ) -> None:
        self._blob_det_params = blob_det_params
        self._blur_kernel = blur_kernel
        self._erosion_kernel = erosion_kernel
        self._erosion_iterations = erosion_iterations
        self._dilation_kernel = dilation_kernel
        self._dilation_iterations = dilation_iterations
        self._moving_foregrouned = moving_foreground

        Stage.__init__(self)

    def execute(self) -> StageResult:
        """
        Detect and returns locations of blobs from foreground mask
        Returns list of coordinates
        """
        foreground_mask = self._moving_foregrouned.moving_foreground.get_frame()

        # Morphological operations
        foreground_mask = self._remove_noise(foreground_mask)

        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(self._blob_det_params)

        # DETECT BLOBS

        # invert image (blob detection only works with white background)
        foreground_mask = cv2.bitwise_not(foreground_mask)

        # apply blur
        foreground_mask = cv2.blur(foreground_mask, self._blur_kernel)

        result = detector.detect(foreground_mask)

        return StageResult(True, True)

    def _remove_noise(self, foreground_mask):
        """
        Uses OpenCV morphological transformations to make blobs more defined
        Returns a foreground mask with more defined blobs
        """
        erosion_kernel = np.ones(self._erosion_kernel, np.uint8)
        dilation_kernel = np.ones(self._dilation_kernel, np.uint8)

        foreground_mask = cv2.erode(
            foreground_mask, erosion_kernel, iterations=self._erosion_iterations,
        )
        foreground_mask = cv2.dilate(
            foreground_mask, dilation_kernel, iterations=self._dilation_iterations,
        )

        return foreground_mask
