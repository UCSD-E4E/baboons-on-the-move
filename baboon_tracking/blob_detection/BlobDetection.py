from abc import ABC, abstractmethod
import numpy as np
import cv2

class BlobDetection(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def detect_blobs(self):
        pass
