"""
Image preprocessor that changes to a PCA based color space.
"""

import numpy as np
from sklearn.decomposition import PCA
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@stage("frame_mixin")
@show_result
class FeatureReductionPca(Stage, PreprocessedFrameMixin):
    """
    Image preprocessor that changes to a PCA based color space.
    """

    def __init__(self, frame_mixin: FrameMixin) -> None:
        PreprocessedFrameMixin.__init__(self)
        Stage.__init__(self)

        self._frame_mixin = frame_mixin
        self._pca = None
        self._mean = None

        self.part1 = None
        self.part2 = None
        self.part3 = None

        self.combined = None

    def _get_transformed_frame(self, frame: Frame, idx=0):
        width, height, _ = frame.get_frame().shape

        flat_frame = np.reshape(frame.get_frame(), (width * height, 3))
        # flat_frame -= self._mean
        flat_pca_frame = self._pca.transform(flat_frame)
        self.combined = Frame(flat_pca_frame, frame.get_frame_number())
        if len(flat_pca_frame.shape) == 2:
            flat_pca_frame = flat_pca_frame[:, idx]
        flat_pca_frame = (flat_pca_frame / np.max(flat_pca_frame)) * 255
        flat_pca_frame = np.round(flat_pca_frame).astype(np.uint8)

        return np.reshape(flat_pca_frame, (width, height))

    def execute(self) -> StageResult:
        frame = self._frame_mixin.frame
        width, height, _ = frame.get_frame().shape

        if self._pca is None:
            X = np.reshape(frame.get_frame(), (width * height, 3))
            self._mean = int(np.round(np.mean(X)))
            # X -= self._mean
            self._pca = PCA(n_components=3)
            self._pca.fit(X)

        self.processed_frame = Frame(
            self._get_transformed_frame(frame), frame.get_frame_number()
        )

        self.part1 = Frame(
            self._get_transformed_frame(frame, idx=0), frame.get_frame_number()
        )
        self.part2 = Frame(
            self._get_transformed_frame(frame, idx=1), frame.get_frame_number()
        )
        self.part3 = Frame(
            self._get_transformed_frame(frame, idx=2), frame.get_frame_number()
        )

        return StageResult(True, True)
