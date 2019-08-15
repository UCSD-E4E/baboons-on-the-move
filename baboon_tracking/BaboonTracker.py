from collections import deque

class BaboonTracker():
    """Master object that stores all strategies used to perform object detection and tracking

    Attributes:
        registration (Registration): object storing registration strategy
        foreground_extraction (ForegroundExtraction): object storing foreground extraction strategy
        blob_detection (BlobDetection): object storing blob detection strategy
        object_tracking (ObjectTracking): object storing object tracking strategy
        pool: multithreading pool used across all methods

    """

    def __init__(self, config, **kwargs):
        """Constructor, initializes all strategies if set by kwargs

        Args:
            config: dictionary containing config information
            kwargs: dictionary containing any additional keyword arguments
        """

        self.config = config

        # set strategies, returns None if kwargs not set
        self.registration = kwargs.get('registration')
        self.foreground_extraction = kwargs.get('foreground_extraction')
        self.blob_detection = kwargs.get('blob_detection')
        self.object_tracking = kwargs.get('object_tracking')

        self.history_frames = deque([])
        self.pool = kwargs.get('pool')

    def push_history_frame(self, frame):
        '''Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count, remove the oldest frame

        Args:
            frame: grayscale opencv image frame
        '''
        if len(self.history_frames) == self.config['history_frame_count']:
            self.history_frames.popleft()

        self.history_frames.append(frame)

    def shift_history_frames(self, target_frame):
        '''Shift all history frames to the input frame

        Args:
            target_frame: grayscale opencv image frame to shift all history frames to

        Returns:
            Return all shifted history frames
        '''
        return self.registration.shift_all_frames(target_frame, self.history_frames, pool=self.pool)

    def generate_motion_mask(self, gray, shifted_history_frames, Ms, framecount=0):
        '''Generate the mask of movement for the current frame

        Args:
            gray: grayscale opencv image frame
            shifted_history_frames: list of previous stabilized frames
            Ms: list of transformation matrices corresponding to each shifted history frames
            framecount: current frame number (used for even/odd performance saving)
        '''
        return self.foreground_extraction.generate_mask(gray, shifted_history_frames, Ms, pool=self.pool, framecount=framecount)

    def detect_blobs(self, foreground_mask):
        '''Uses foreground mask to detect blobs

        Args:
            foreground_mask: binary mask representing moving foreground

        Returns:
            Returns list of detected blob coordinates
        '''
        return self.blob_detection.detect_blobs(foreground_mask)
