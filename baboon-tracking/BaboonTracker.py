from registration import registration_strategies
from image_diff import image_diff_strategies

class BaboonTracker():

    def __init__(self, configs, pool=None):
        self.registration_strategy = registration_strategies[configs['registration_strategy']]
        self.image_diff_strategy = None
        self.blob_tracking_strategy = None

        self.history_frames = deque([])
        self.pool = pool

    def push_history_frame(self, frame):
        '''
        Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count,
        remove the oldest frame
        '''
        if len(self.history_frames) == HISTORY_FRAME_COUNT:
            self.history_frames.popleft()

        self.history_frames.append(frame)

    def shift_history_frames(self):
        '''
        Shift all history frames to the latest frame
        Return all shifted history frames 
        '''
        target_frame = self.history_frames[-1]
        frames = self.history_frames[:-1]

        return self.registration_strategy.shift_all_frames(target_frame, frames, pool)
        
    def generate_motion_mask(self, shifted_history_frames, Ms, pool):
        '''
        Generate the mask of movement for the current frame
        '''
        return self.image_diff_strategy.generate_mask(shifted_history_frames, Ms, pool)
