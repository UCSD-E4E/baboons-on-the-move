from collections import deque

from .registration import registration_strategies
from .image_diff import image_diff_strategies
from .object_tracking import object_tracking_strategies

class BaboonTracker():

    def __init__(self, config, pool=None):
        self.registration_strategy = registration_strategies[config['registration_strategy']](config)
        self.image_diff_strategy = image_diff_strategies[config['image_diff_strategy']](config)
        self.blob_tracking_strategy = None

        self.config = config
        self.history_frames = deque([])
        self.pool = pool

    def push_history_frame(self, frame):
        '''
        Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count,
        remove the oldest frame
        '''
        if len(self.history_frames) == self.config['history_frame_count']:
            self.history_frames.popleft()

        self.history_frames.append(frame)

    def shift_history_frames(self, target_frame):
        '''
        Shift all history frames to the input frame
        Return all shifted history frames 
        '''
        return self.registration_strategy.shift_all_frames(target_frame, self.history_frames, pool=self.pool)
        
    def generate_motion_mask(self, gray, shifted_history_frames, Ms):
        '''
        Generate the mask of movement for the current frame
        '''
        return self.image_diff_strategy.generate_mask(gray, shifted_history_frames, Ms, pool=self.pool)
