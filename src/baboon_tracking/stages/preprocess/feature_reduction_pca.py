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

    def execute(self) -> StageResult:
        frame = self._frame_mixin.frame
        width, height, _ = frame.get_frame().shape

        if self._pca is None:
            X = np.reshape(frame.get_frame(), (width * height, 3))
            self._pca = PCA(n_components=1)
            self._pca.fit(X)

        flat_frame = np.reshape(frame.get_frame(), (width * height, 3))
        flat_pca_frame = self._pca.transform(flat_frame)
        flat_pca_frame = (flat_pca_frame / np.max(flat_pca_frame)) * 255
        flat_pca_frame = np.round(flat_pca_frame).astype(np.uint8)
        pca_frame = np.reshape(flat_pca_frame, (width, height))

        self.processed_frame = Frame(pca_frame, frame.get_frame_number())

        return StageResult(True, True)
