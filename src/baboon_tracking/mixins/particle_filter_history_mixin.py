from abc import ABC, abstractproperty
from typing import List, Tuple

from baboon_tracking.models.particle_filter import Particle


class ParticleFilterHistoryMixin(ABC):
    @abstractproperty
    def particle_filter_history(
        self,
    ) -> List[Tuple[int, List[Tuple[int, str, List[Particle]]]]]:
        raise NotImplementedError
