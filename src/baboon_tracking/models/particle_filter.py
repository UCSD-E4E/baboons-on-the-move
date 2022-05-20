from math import cos, pi, sin, sqrt
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

    def transform(self, transformation: np.ndarray):
        x1, y1, x2, y2 = self.baboon.rectangle

        top_left = np.array([x1, y1, 1])
        bottom_right = np.array([x2, y2, 1])

        top_left = np.round(np.matmul(transformation, top_left)).astype(np.int32)
        bottom_right = np.round(np.matmul(transformation, bottom_right)).astype(
            np.int32
        )

        self.baboon = Baboon(
            (top_left[0], top_left[1], bottom_right[0], bottom_right[1]),
            id_str=self.baboon.id_str,
            identity=self.baboon.identity,
        )

    def predict(self):
        x1, y1, x2, y2 = self.baboon.rectangle
        width = x2 - x1
        height = y2 - y1
        length = sqrt(width**2 + height**2)

        sample = np.abs(np.random.normal(scale=0.01)) * length
        degs = random() * 2 * pi

        val = 1
        half_val = val / 2.0

        delta_x = int(np.asscalar(np.round(sample * sin(degs))))
        delta_y = int(np.asscalar(np.round(sample * cos(degs))))

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

    def update(self, baboons: List[Baboon]):
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
        self.baboon = baboon

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

        return Baboon(
            (x1, y1, x2, y2), id_str=self.baboon.id_str, identity=self.baboon.identity
        )


class ParticleFilter:
    instance_id = 0

    def __init__(self, baboon: Baboon, particle_count: int):
        self._particle_count = particle_count
        self._weight = 1.0 / float(particle_count)

        self.particles: List[Particle] = [
            Particle(baboon, self._weight) for _ in range(particle_count)
        ]

        self._instance_id = ParticleFilter.instance_id
        ParticleFilter.instance_id += 1

        baboon.identity = self._instance_id
        baboon.id_str = str(self._instance_id)

    def transform(self, transformation: np.ndarray):
        for particle in self.particles:
            particle.transform(transformation)

    def predict(self):
        for particle in self.particles:
            particle.predict()

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
