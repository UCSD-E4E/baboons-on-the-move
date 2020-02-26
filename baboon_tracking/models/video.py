import cv2
import yaml
from baboon_tracking.models.frame import Frame

class Video():   

    def __init__(self):
        self.curr_frame = 0
        self.cap = None

    def get_cap( self ):
        return self.cap

    def next_frame( self ):
        if self.cap is not None:  
            success, raw_frame = self.cap.read()
            frame_obj = Frame( raw_frame, self.curr_frame )

            self.curr_frame += 1

            return (success, frame_obj)

    def release( self ):
        if self.cap is not None:
            self.cap.release()
    
# Responsible for understanding the video 
class InputVideo(Video):

    # Load the data into this Configuration Object
    def __init__(self, input_location):
        super().__init__()

        # open the input video
        self.cap = cv2.VideoCapture( input_location )

        if not self.cap.isOpened():
            print( "Error opening video stream or file: ", input_location )
            exit()
        
        self._load_metadata( self.cap )  
        self.curr_frame = 0

    # A different responsibility from the Config object in the making
    def _load_metadata( self, cap ):
        self.frame_width    = int( cap.get( cv2.CAP_PROP_FRAME_WIDTH ) )
        self.frame_height   = int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT ) )
        self.fps            = cap.get( cv2.CAP_PROP_FPS )
        self.frame_count    = cap.get( cv2.CAP_PROP_FRAME_COUNT )
        self.video_length   = self.frame_count / self.fps

# Responsible for understanding the video 
class OutputVideo(Video):

    # Load the data into this Configuration Object
    def __init__(self, output_location, fps, frame_width, frame_height ):
        super().__init__()

        # create the output video
        self.cap = cv2.VideoWriter( output_location, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        self.output_location = output_location
        self.frame_width     = frame_width
        self.frame_height    = frame_height
        self.fps             = fps

    def write( self, frame ):
        self.cap.write( frame )
