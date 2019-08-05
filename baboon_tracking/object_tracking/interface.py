from abc import ABC, abstractmethod

class TrackingStrategy(ABC):
    def __init__(self, config):
        self.config = config
