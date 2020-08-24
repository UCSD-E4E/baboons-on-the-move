from abc import ABC, abstractmethod
import cv2
import numpy as np
import math


class ForegroundExtraction(ABC):
    def __init__(self, history_frames):
        self.history_frames = history_frames

    @abstractmethod
    def generate_mask(self):
        pass
