from abc import ABC, abstractmethod
import cv2
import numpy as np
import math

class ForegroundExtractionStrategy(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def generate_mask(self):
        pass
