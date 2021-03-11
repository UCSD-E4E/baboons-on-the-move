"""
Generates a set of weights to represent how often a pixel changes.
"""
import numpy as np
from baboon_tracking.mixins.quantized_frames_mixin import QuantizedFramesMixin
from baboon_tracking.mixins.weights_mixin import WeightsMixin
from baboon_tracking.stages.motion_detector import (
    generate_weights_c
)
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage


@stage("quantized_frames")
class GenerateWeights(Stage, WeightsMixin):
    """
    Generates a set of weights to represent how often a pixel changes.
    """

    def __init__(self, quantized_frames: QuantizedFramesMixin) -> None:
        Stage.__init__(self)
        WeightsMixin.__init__(self)

        self._quantized_frames = quantized_frames

    def execute(self) -> StageResult:
        quantized_frames = self._quantized_frames.quantized_frames

        #self.weights = self._get_weights(quantized_frames)
        self.weights = generate_weights_c.get_weights(quantized_frames)

        return StageResult(True, True)

    def _get_weights(self, q_frames):
        """
        Calculate weights based on frequency of commonality between frames according
        to figure 12 of paper
        Returns frame representing frequency of commonality
        """
        #return self.parallel_masks(q_frames)
        weights = np.zeros(q_frames[0].shape).astype(np.uint8)

        for i, _ in enumerate(q_frames):
            if i == 0:
                continue

            mask = (np.abs(q_frames[i] - q_frames[i - 1]) <= 1).astype(np.uint8)
            weights = weights + mask

        return weights
    '''
    @staticmethod
    #@njit(parallel=True, cache=True)
    def parallel_masks(q_frames):
        masks = np.empty((len(q_frames),) + q_frames[0].shape, dtype=np.uint8)
        for i in range(1, len(q_frames)):
            masks[i] = (np.abs(q_frames[i] - q_frames[i - 1]) <= 1).astype(np.uint8)

        return np.sum(masks, axis=0)
    '''
