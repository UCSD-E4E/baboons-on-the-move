import cv2
import numpy as np
import math

from .ForegroundExtraction import ForegroundExtraction

class SimpleBackgroundSub_ForegroundExtraction(ForegroundExtraction):
    '''
    Using simple python background subtraction
    '''

    def generate_mask(self):
        raise NotImplementedError()
