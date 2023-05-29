"""
Implements a particle filter.
"""

from math import cos, pi, sin, sqrt
from multiprocessing import Semaphore
from random import random
from typing import Dict, List, Tuple
import numpy as np

from baboon_tracking.models.region import Region
from baboon_tracking.models.bayesian_region import BayesianRegion
from library.region import bb_intersection_over_union


class Particle:
    """
    Implements a particle for a particle filter.
    """

    def __init__(self, baboon: BayesianRegion, weight: float):
        self.baboon = baboon
        self.weight = weight

    def transform(self, transformation: np.ndarray):
        """
        Transforms the location of the particle using the specified transform.
        """

        x1, y1, x2, y2 = self.baboon.rectangle

        top_left = np.array([x1, y1, 1])
        bottom_right = np.array([x2, y2, 1])

        top_left = np.round(np.matmul(transformation, top_left)).astype(np.int32)
        bottom_right = np.round(np.matmul(transformation, bottom_right)).astype(
            np.int32
        )

        self.baboon = BayesianRegion(
            (top_left[0], top_left[1], bottom_right[0], bottom_right[1]),
            id_str=self.baboon.id_str,
            identity=self.baboon.identity,
            observed=self.baboon.observed,
        )

    def predict(self):
        """
        Moves the particle using our best guess of where we expect the region to be.
        """

        x1, y1, x2, y2 = self.baboon.rectangle
        width = x2 - x1
        height = y2 - y1
        length = sqrt(width**2 + height**2)

        sample = np.abs(np.random.normal(scale=0.01)) * length
        degs = random() * 2 * pi

        val = 1
        half_val = val / 2.0

        delta_x = int(np.round(sample * sin(degs)).item())
        delta_y = int(np.round(sample * cos(degs)).item())

        delta_x1 = int(round(random() * val - half_val))
        delta_y1 = int(round(random() * val - half_val))
        delta_x2 = int(round(random() * val - half_val))
        delta_y2 = int(round(random() * val - half_val))

        if delta_x1 >= delta_x2:
            delta_x2 = delta_x1

        if delta_y1 >= delta_y2:
            delta_y2 = delta_y1

        self.baboon = self._get_moved_baboon(
            delta_x, delta_y, delta_x1, delta_y1, delta_x2, delta_y2
        )
        self.baboon.observed = False

    def update(self, baboons: List[Region]):
        """
        Moves the region based on our observations.
        """

        baboons = [
            (bb_intersection_over_union(self.baboon.rectangle, b.rectangle), b)
            for b in baboons
        ]
        baboons.sort(key=lambda b: b[0], reverse=True)

        weight, baboon = baboons[0]

        if weight == 0:
            return

        baboon.id_str = self.baboon.id_str
        baboon.identity = self.baboon.identity

        self.weight *= weight
        self.baboon = BayesianRegion.from_region(baboon, observed=True)

    def _get_moved_baboon(
        self,
        delta_x: int,
        delta_y: int,
        delta_x1: int,
        delta_y1: int,
        delta_x2: int,
        delta_y2: int,
    ):
        x1, y1, x2, y2 = self.baboon.rectangle

        x1 += delta_x
        y1 += delta_y

        x2 += delta_x
        y2 += delta_y

        x1 += delta_x1
        y1 += delta_y1

        x2 += delta_x2
        y2 += delta_y2

        return BayesianRegion(
            (x1, y1, x2, y2),
            id_str=self.baboon.id_str,
            identity=self.baboon.identity,
            observed=self.baboon.observed,
        )


class ParticleFilter:
    """
    Implements a particle filter.
    """

    _instance_id = 0
    _lock = Semaphore()

    def __init__(self, baboon: Region, particle_count: int):
        self._particle_count = particle_count
        self._weight = 1.0 / float(particle_count)
        self._particle_history_idx = 0
        self._particle_history: List[Tuple[int, str, List[Particle]]] = []

        bayesian_baboon = BayesianRegion.from_region(baboon, observed=True)
        self.particles: List[Particle] = [
            Particle(bayesian_baboon, self._weight) for _ in range(particle_count)
        ]
        self._add_particle_history("initial", self.particles)

        with ParticleFilter._lock:
            self.instance_id = ParticleFilter._instance_id
            ParticleFilter._instance_id += 1

        bayesian_baboon.identity = self.instance_id
        bayesian_baboon.id_str = str(self.instance_id)

    @property
    def particle_history(self):
        return self._particle_history

    def _add_particle_history(self, step_name: str, particles: List[Particle]):
        self._particle_history.append(
            (self._particle_history_idx, step_name, particles)
        )
        self._particle_history_idx += 1

    def transform(self, transformation: np.ndarray):
        """
        Transforms each particle using the specified transformation matrix.
        """
        for particle in self.particles:
            particle.transform(transformation)

        self._add_particle_history("transform", self.particles)

    def predict(self):
        """
        Performs the predict step on each of the particles.
        """
        for particle in self.particles:
            particle.predict()

        self._add_particle_history("predict", self.particles)

    def update(self, baboons: List[Region]):
        """
        Performs the update step on each of the particles.
        """
        for particle in self.particles:
            particle.update(baboons)

        self._add_particle_history("update", self.particles)

    def resample(self):
        """
        Resamples the particles to have the required weights.
        """
        baboon_weights: Dict[BayesianRegion, float] = {}

        for particle in self.particles:
            if not particle.baboon in baboon_weights:
                baboon_weights[particle.baboon] = 0.0

            baboon_weights[particle.baboon] += particle.weight

        normalizer = np.sum(np.array([w for _, w in baboon_weights.items()]))
        baboons_weights = list((b, w) for b, w in baboon_weights.items())
        baboons_weights.sort(key=lambda x: x[1], reverse=True)

        self.particles = []
        count = 0
        for baboon, weight in baboons_weights:
            particle_count = int(np.round((weight / normalizer) / self._weight).item())

            if count + particle_count > self._particle_count:
                particle_count = self._particle_count - count

            if particle_count == 0:
                break

            self.particles.extend(
                [Particle(baboon, self._weight) for _ in range(particle_count)]
            )

            count = len(self.particles)

        self._add_particle_history("resample", self.particles)

    def get_baboon(self) -> Region:
        """
        Gets the most likely baboon from the particle filter.
        """

        baboon_weights: Dict[BayesianRegion, float] = {}

        for particle in self.particles:
            if not particle.baboon in baboon_weights:
                baboon_weights[particle.baboon] = 0.0

            baboon_weights[particle.baboon] += particle.weight

        weights_and_baboons = [(w, b) for b, w in baboon_weights.items()]
        _, baboon = max(weights_and_baboons, key=lambda x: x[0])

        return baboon

    def get_probability(self, baboon: Region):
        """
        Gets the probability that this baboon is represented by the particle filter.
        """

        return np.sum(
            (
                np.array(
                    [
                        bb_intersection_over_union(p.baboon.rectangle, baboon.rectangle)
                        for p in self.particles
                    ]
                )
                * self._weight
            )
        )
