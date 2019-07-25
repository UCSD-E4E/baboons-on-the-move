from collections import deque

from .registration import registration_strategies
from .foreground_extraction import foreground_extraction_strategies
from .blob_detection import blob_detection_strategies
from .object_tracking import object_tracking_strategies

class BaboonTracker():

    def __init__(self, config, pool=None):
        self.registration_strategy = registration_strategies[config['registration_strategy']](config)
        self.foreground_extraction_strategy = foreground_extraction_strategies[config['foreground_extraction_strategy']](config)
        self.blob_detection_strategy = blob_detection_strategies[config['blob_detection_strategy']](config)
        self.object_tracking_strategy = object_tracking_strategies[config['object_tracking_strategy']](config)

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
        return self.foreground_extraction_strategy.generate_mask(gray, shifted_history_frames, Ms, pool=self.pool)

    def detect_blobs(self, foreground_mask):
        '''
        Uses foreground mask to detect blobs
        Returns list of detected blob coordinates
        '''
        return self.blob_detection_strategy.detect_blobs(foreground_mask)