from typing import Tuple
from baboon_tracking.models.region import Region


class BayesianRegion(Region):
    def __init__(
        self,
        rectange: Tuple[int, int, int, int],
        id_str: str = None,
        identity: int = None,
        observed=False,
    ):
        Region.__init__(self, rectange, id_str=id_str, identity=identity)

        self.observed = observed

    @staticmethod
    def from_region(region: Region, observed=False):
        return BayesianRegion(
            region.rectangle,
            id_str=region.id_str,
            identity=region.identity,
            observed=observed,
        )
