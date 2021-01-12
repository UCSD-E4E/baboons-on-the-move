"""
Implements a motion tracker pipeline.
"""

from baboon_tracking.stages.detect_blobs import DetectBlobs
from baboon_tracking.stages.motion_detector.apply_masks import ApplyMasks
from baboon_tracking.stages.motion_detector.compute_moving_foreground import (
    ComputeMovingForeground,
)
from baboon_tracking.stages.motion_detector.compute_transformation_matrices import (
    ComputeTransformationMatrices,
)
from baboon_tracking.stages.motion_detector.generate_mask_subcomponents.generate_mask_subcomponents import (
    GenerateMaskSubcomponents,
)
from baboon_tracking.stages.motion_detector.generate_weights import GenerateWeights
from baboon_tracking.stages.motion_detector.noise_reduction import NoiseReduction
from baboon_tracking.stages.motion_detector.quantize_history_frames import (
    QuantizeHistoryFrames,
)
from baboon_tracking.stages.motion_detector.transformed_frames.transformed_frames import (
    TransformedFrames,
)
from baboon_tracking.stages.motion_detector.store_history_frame import StoreHistoryFrame

# from baboon_tracking.stages.save_video import SaveVideo
from baboon_tracking.stages.show_last_frame import ShowLastFrame
from pipeline import Serial


class MotionDetector(Serial):
    """
    Implements a motion tracker pipeline.
    """

    def __init__(self):
        Serial.__init__(
            self,
            "MotionDetector",
            StoreHistoryFrame,
            ComputeTransformationMatrices,
            TransformedFrames,
            QuantizeHistoryFrames,
            GenerateWeights,
            GenerateMaskSubcomponents,
            ComputeMovingForeground,
            ApplyMasks,
            NoiseReduction,
            # SaveVideo,
            DetectBlobs,
            ShowLastFrame,
        )
