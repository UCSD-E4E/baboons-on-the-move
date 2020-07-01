from .models import Frame

class BaboonTracker():
    """Master object that stores all strategies used to perform object detection and tracking

    Attributes:
        registration (Registration): object storing registration strategy
        foreground_extraction (ForegroundExtraction): object storing foreground extraction strategy
        blob_detection (BlobDetection): object storing blob detection strategy
        object_tracking (ObjectTracking): object storing object tracking strategy

    """

    def __init__(self, **kwargs):
        """Constructor, initializes all strategies if set by kwargs

        Args:
            config: dictionary containing config information
            kwargs: dictionary containing any additional keyword arguments
        """

        # set strategies, kwargs.get() returns None if kwargs not set
        self.registration = kwargs.get('registration')
        self.foreground_extraction = kwargs.get('foreground_extraction')
        self.blob_detection = kwargs.get('blob_detection')
        self.object_tracking = kwargs.get('object_tracking')

    def is_history_frames_full(self):
        return self.registration.is_history_frames_full()

    def push_history_frame(self, frame: Frame):
        self.registration.push_history_frame(frame)

    def shift_history_frames(self, target_frame: Frame):
        '''Shift all history frames to the input frame

        Args:
            target_frame: grayscale opencv image frame to shift all history frames to

        Returns:
            Return all shifted history frames
        '''
        return self.registration.shift_all_frames(target_frame)

    def generate_motion_mask(self, gray: Frame, shifted_history_frames, Ms):
        '''Generate the mask of movement for the current frame

        Args:
            gray: grayscale opencv image frame
            shifted_history_frames: list of previous stabilized frames
            Ms: list of transformation matrices corresponding to each shifted history frames
        '''
        return self.foreground_extraction.generate_mask(gray, shifted_history_frames, Ms)

    def detect_blobs(self, foreground_mask):
        '''Uses foreground mask to detect blobs

        Args:
            foreground_mask: binary mask representing moving foreground

        Returns:
            Returns list of detected blob coordinates
        '''
        return self.blob_detection.detect_blobs(foreground_mask)
