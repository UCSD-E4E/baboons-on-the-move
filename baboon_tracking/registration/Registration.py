from abc import ABC, abstractmethod
import cv2
import numpy as np
import math
import cmath

from ..models import Frame

class Registration(ABC):
    def __init__(self, config):
        self.MAX_FEATURES = config['registration']['max_features']
        self.GOOD_MATCH_PERCENT = config['registration']['good_match_percent']
        self.config = config

    def _shift_frame(self, frames):#, frame, previous_frame):
        '''
        Takes in transformation matrix; does homography transformation to register/align two frames
        '''
        frame: Frame = frames[0]
        previous_frame: Frame = frames[1]

        M = self.register(previous_frame, frame)
        #return (previous_frame, M)
        return (Frame(cv2.warpPerspective(previous_frame.get_frame(), M, (previous_frame.get_frame().shape[1], previous_frame.get_frame().shape[0])).astype(np.uint8), previous_frame.get_frame_number()), M)

    @abstractmethod
    def register(self, frame1: Frame, frame2: Frame):
        pass

    def shift_all_frames(self, target_frame, frames):
        '''
        Shifts all frames to target frame, returns list of shifted frames
        '''
        return [self._shift_frame((target_frame, f)) for f in frames]
