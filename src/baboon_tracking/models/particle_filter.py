from math import cos, pi, sin
import numpy as np

from typing import Dict, List
from pickle import load
from baboon_tracking.models.baboon import Baboon
from library.region import bb_intersection_over_union
from sklearn.mixture import BayesianGaussianMixture
from random import random


class Particle:
    def __init__(self, baboon: Baboon, weight: float):
        self.baboon = baboon
        self.weight = weight

    def predict(self, model: BayesianGaussianMixture):
        sample, _ = model.sample()
        degs = random() * 2 * pi

        x = int(np.asscalar(np.round(sample * sin(degs))))
        y = int(np.asscalar(np.round(sample * cos(degs))))

        self.baboon = self._get_moved_baboon(x, y)

    def update(self, baboons: List[Baboon]):
        baboons = [
            (bb_intersection_over_union(self.baboon.rectangle, b.rectangle), b)
            for b in baboons
        ]
        baboons.sort(key=lambda b: b[0], reverse=True)

        weight, baboon = baboons[0]

        if weight == 0:
            return

        self.weight *= weight
        self.baboon = baboon

    def _get_moved_baboon(self, delta_x: int, delta_y: int):
        x1, y1, x2, y2 = self.baboon.rectangle

        x1 += delta_x
        y1 += delta_y

        x2 += delta_x
        y2 += delta_y

        return Baboon(
            (x1, y1, x2, y2), id_str=self.baboon.id_str, identity=self.baboon.identity
        )


class ParticleFilter:
    def __init__(self, baboon: Baboon, particle_count: int):
        self._particle_count = particle_count
        self._weight = 1.0 / float(particle_count)

        with open("./displacement_mixture.pickle", "rb") as f:
            self._model: BayesianGaussianMixture = load(f)

        self.particles: List[Particle] = [
            Particle(baboon, self._weight) for _ in range(particle_count)
        ]

    def predict(self):
        for particle in self.particles:
            particle.predict(self._model)

    def update(self, baboons: List[Baboon]):
        for particle in self.particles:
            particle.update(baboons)

    def resample(self):
        baboon_weights: Dict[Baboon, float] = {}

        for particle in self.particles:
            if not particle.baboon in baboon_weights:
                baboon_weights[particle.baboon] = 0.0

            baboon_weights[particle.baboon] += particle.weight

        normalizer = np.sum(np.array([baboon_weights[b] for b in baboon_weights]))
        baboons_weights = [(b, baboon_weights[b]) for b in baboon_weights]
        baboons_weights.sort(key=lambda x: x[1], reverse=True)

        self.particles = []
        count = 0
        for baboon, weight in baboons_weights:
            particle_count = int(
                np.asscalar(np.round((weight / normalizer) / self._weight))
            )

            if count + particle_count > self._particle_count:
                particle_count = self._particle_count - count

            if particle_count == 0:
                break

            self.particles.extend(
                [Particle(baboon, self._weight) for _ in range(particle_count)]
            )

            count = len(self.particles)

    def get_baboon(self):
        baboon_weights: Dict[Baboon, float] = {}

        for particle in self.particles:
            if not particle.baboon in baboon_weights:
                baboon_weights[particle.baboon] = 0.0

            baboon_weights[particle.baboon] += particle.weight

        weights_and_baboons = [(baboon_weights[b], b) for b in baboon_weights]
        _, baboon = max(weights_and_baboons, key=lambda x: x[0])

        return baboon

    def get_probability(self, baboon: Baboon):
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
