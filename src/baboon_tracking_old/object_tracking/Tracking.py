from abc import ABC, abstractmethod


class Tracking(ABC):
    def __init__(self, config):
        self.config = config
