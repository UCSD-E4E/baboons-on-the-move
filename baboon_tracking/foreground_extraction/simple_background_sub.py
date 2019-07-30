import cv2
import numpy as np
import math

from .interface import ForegroundExtractionStrategy

class SimpleBackgroundSub_ForegroundExtractionStrategy(ForegroundExtractionStrategy):
    '''
    Using simple python background subtraction
    '''

    def generate_mask(self):
        raise NotImplementedError()
