import concurrent.futures

from typing import List, Set

from numpy import ndarray
from baboon_tracking.decorators.debug import debug
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from baboon_tracking.models.baboon import Baboon
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.particle_filter import ParticleFilter
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage


flatten = lambda t: [item for sublist in t for item in sublist]


def process_pool(
    particle_filter: ParticleFilter,
    baboons: BaboonsMixin,
    transformation_matrix: ndarray,
):
    particle_filter.predict()

    if transformation_matrix is not None:
        particle_filter.transform(transformation_matrix)

    particle_filter.update(baboons)
    particle_filter.resample()


@debug(FrameMixin, (0, 0, 255))
@stage("baboons")
@stage("transformation_matrices")
class ParticleFilterStage(Stage, BaboonsMixin):
    def __init__(
        self,
        baboons: BaboonsMixin,
        transformation_matrices: TransformationMatricesMixin,
    ) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._executor = concurrent.futures.ProcessPoolExecutor()
        self._baboons = baboons
        self._transformation_matrices = transformation_matrices
        self._particle_filters: List[ParticleFilter] = []
        self._particle_count = 5
        self._probability_thresh = 0

    def on_destroy(self) -> None:
        self._executor.shutdown()

    def execute(self) -> StageResult:
        # self._executor.map(
        #     process_pool,
        #     self._particle_filters,
        #     [self._baboons.baboons for _ in self._particle_filters],
        #     [self._transformation_matrices for _ in self._particle_filters],
        # )
        for particle_filter in self._particle_filters:
            process_pool(
                particle_filter,
                self._baboons.baboons,
                self._transformation_matrices.current_frame_transformation,
            )

        probs = [
            [(p.get_probability(b), b) for b in self._baboons.baboons]
            for p in self._particle_filters
        ]
        probs = flatten(probs)
        probs.sort(key=lambda p: p[0], reverse=True)
        probs = [(p, b) for p, b in probs if p > self._probability_thresh]

        used_babooons: Set[Baboon] = set()
        for _, baboon in probs:
            if baboon in used_babooons:
                continue

            used_babooons.add(baboon)

        unused_baboons = [b for b in self._baboons.baboons if not b in used_babooons]

        self._particle_filters.extend(
            [ParticleFilter(b, self._particle_count) for b in unused_baboons]
        )

        self.baboons = [p.get_baboon() for p in self._particle_filters]

        return StageResult(True, True)
