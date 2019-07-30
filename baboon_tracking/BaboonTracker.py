from collections import deque

class BaboonTracker():
    # TODO: USE KWARGS!
    def __init__(self, config, registration=None, foreground_extraction=None, blob_detection=None, object_tracking=None, pool=None):

        self.config = config

        # set strategies
        self.registration_strategy = registration if (registration is not None) else None
        self.foreground_extraction_strategy = foreground_extraction if (foreground_extraction is not None) else None
        self.blob_detection_strategy = blob_detection if (blob_detection is not None) else None
        self.object_tracking_strategy = object_tracking if (object_tracking is not None) else None

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

    def generate_motion_mask(self, gray, shifted_history_frames, Ms, framecount=0):
        '''
        Generate the mask of movement for the current frame
        '''
        return self.foreground_extraction_strategy.generate_mask(gray, shifted_history_frames, Ms, pool=self.pool, framecount=framecount)

    def detect_blobs(self, foreground_mask):
        '''
        Uses foreground mask to detect blobs
        Returns list of detected blob coordinates
        '''
        return self.blob_detection_strategy.detect_blobs(foreground_mask)
