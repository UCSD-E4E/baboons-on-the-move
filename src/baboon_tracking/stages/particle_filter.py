import concurrent.futures

from typing import List, Set
from baboon_tracking.models.baboon import Baboon
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.particle_filter import ParticleFilter
from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.decorators import stage


flatten = lambda t: [item for sublist in t for item in sublist]


def process_pool(particle_filter: ParticleFilter, baboons: BaboonsMixin):

    particle_filter.predict()
    particle_filter.update(baboons)
    particle_filter.resample()

    return particle_filter


@stage("baboons")
class ParticleFilterStage(Stage, BaboonsMixin):
    def __init__(self, baboons: BaboonsMixin) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._executor = concurrent.futures.ProcessPoolExecutor()
        self._baboons = baboons
        self._particle_filters: List[ParticleFilter] = []
        self._particle_count = 500
        self._probability_thresh = 0.5

    def on_destroy(self) -> None:
        self._executor.shutdown()

    def execute(self) -> StageResult:

        self._executor.map(process_pool, self._particle_filters, self._baboons.baboons)

        probs = [
            [(p.get_probability(b), b) for b in self._baboons.baboons]
            for p in self._particle_filters
        ]
        probs = flatten(probs)
        probs.sort(key=lambda p: p[0], reverse=True)
        probs = [(p, b) for p, b in probs if p >= self._probability_thresh]

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
