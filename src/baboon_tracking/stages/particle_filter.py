"""
Defines a stage which uses a paticle filter to fill in missing regions.
"""

import concurrent.futures

from typing import List, Set

from numpy import ndarray
from baboon_tracking.decorators.debug import debug
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from baboon_tracking.models.region import Region
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.particle_filter import ParticleFilter
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage


flatten = lambda t: [item for sublist in t for item in sublist]


def process_pool(
    particle_filter: ParticleFilter,
    baboons: List[Region],
    transformation_matrix: ndarray,
):
    """
    Runs particle filter steps.
    """

    particle_filter.predict()

    if transformation_matrix is not None:
        particle_filter.transform(transformation_matrix)

    particle_filter.update(baboons)
    particle_filter.resample()

    return particle_filter


@debug(FrameMixin, (0, 0, 255))
@stage("baboons")
@stage("transformation_matrices")
class ParticleFilterStage(Stage, BaboonsMixin):
    """
    Defines a stage which uses a paticle filter to fill in missing regions.
    """

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
        self._particle_filters: Set[ParticleFilter] = {}
        self._particle_count = 5
        self._probability_thresh = 0

    def on_destroy(self) -> None:
        self._executor.shutdown()

    def execute(self) -> StageResult:
        futures = [
            self._executor.submit(
                process_pool,
                p,
                self._baboons.baboons,
                self._transformation_matrices.current_frame_transformation,
            )
            for p in self._particle_filters
        ]
        self._particle_filters = {f.result() for f in futures}

        probs = [
            [(p.get_probability(b), b, p) for b in self._baboons.baboons]
            for p in self._particle_filters
        ]
        probs = flatten(probs)
        probs.sort(key=lambda p: p[0], reverse=True)

        used_particle_filters = {
            pf for p, _, pf in probs if p > self._probability_thresh
        }
        unused_particle_filters = [
            p for p in self._particle_filters if p not in used_particle_filters
        ]
        self._particle_filters.difference_update(unused_particle_filters)

        thresh_probs = [(p, b) for p, b, _ in probs if p > self._probability_thresh]
        used_babooons: Set[Region] = set()
        for _, baboon in thresh_probs:
            if baboon in used_babooons:
                continue

            used_babooons.add(baboon)

        unused_baboons = [b for b in self._baboons.baboons if not b in used_babooons]

        self._particle_filters.update(
            ParticleFilter(b, self._particle_count) for b in unused_baboons
        )

        self.baboons = [p.get_baboon() for p in self._particle_filters]

        return StageResult(True, True)
