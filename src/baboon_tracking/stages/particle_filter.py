import multiprocessing
from typing import List, Set
from baboon_tracking.models.baboon import Baboon
from pipeline import Stage
from pipeline.stage_result import StageResult
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.models.particle_filter import ParticleFilter
from pipeline.decorators import stage


from baboon_tracking.models.particle_filter import ParticleFilter
from multiprocessing import shared_memory

import concurrent.futures
import time

flatten = lambda t: [item for sublist in t for item in sublist]


def ProcessPool(filter: ParticleFilter, baboons: BaboonsMixin):

    filter.predict()
    filter.update(baboons)
    filter.resample()


@stage("baboons")
class ParticleFilterStage(Stage, BaboonsMixin):
    def __init__(self, baboons: BaboonsMixin) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)

        self._baboons = baboons
        self._particle_filters: List[ParticleFilter] = []
        self._particle_count = 5
        self._probability_thresh = 0.6

    def execute(self) -> StageResult:

        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     executor.map(ProcessPool, self._particle_filters, self._baboons.baboons)

        for particle_filter in self._particle_filters:
            # multiprocessing.Process(particle_filter.predict()).start
            particle_filter.predict()
            particle_filter.update(self._baboons.baboons)
            particle_filter.resample()

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

        time.process_time()

        return StageResult(True, True)

