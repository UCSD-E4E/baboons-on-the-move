from typing import Dict
from baboon_tracking.stages.particle_filter.get_baboons import GetBaboons
from baboon_tracking.stages.particle_filter.predict import Predict
from baboon_tracking.stages.particle_filter.resample import Resample
from baboon_tracking.stages.particle_filter.update import Update
from pipeline import Serial
from pipeline.decorators import runtime_config


@runtime_config("rconfig")
class ParticleFilter(Serial):
    def __init__(self, rconfig: Dict[str, any]) -> None:
        Serial.__init__(
            self, "ParticleFilter", rconfig, Predict, Update, Resample, GetBaboons
        )

