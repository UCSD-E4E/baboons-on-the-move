from registration import registration_strategies
from image_diff import image_diff_strategies

class BaboonTracker():

    def __init__(self, configs, pool=None):
        self.registration_strategy = registration_strategies[configs['registration_strategy']]
        self.image_diff_strategy = None
        self.blob_tracking_strategy = None

        self.history_frames = deque([])
        self.pool = pool

    def push_history_frame(frame):
        '''
        Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count,
        remove the oldest frame
        '''
        if len(self.history_frames) == HISTORY_FRAME_COUNT:
            self.history_frames.popleft()

        self.history_frames.append(frame)

    def shift_history_frames():
        '''
        Shift all history frames to the latest frame
        Return all shifted history frames 
        '''
        target_frame = self.history_frames[-1]
        frames = self.history_frames[:-1]

        if(pool is not None):
            print("shifting history frames (non-multiprocessing)")
           return self.registration_strategy.shift_all_frames_multiprocessing(target_frame, frames, pool)
        else:
            print("shifting history frames (multiprocessing)")
            return self.registration_strategy.shift_all_frames(target_frame, frames)

    def generate_motion_mask():
        '''
        Generate the mask of movement for the current frame
        '''
