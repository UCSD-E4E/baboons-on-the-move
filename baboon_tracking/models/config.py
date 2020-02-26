import cv2
import yaml

# Responsible for understanding the format of the configuration file
class Config:

    # Load the data into this Configuration Object
    def __init__(self, config_uri):
        super().__init__()

        with open( config_uri, 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
                self.registration    = self.config['registration']
                self.display_width   = self.config['display']['width']
                self.display_height  = self.config['display']['height']
                self.input_location  = self.config['input']
                self.output_location = self.config['output']
                self.max_frames      = self.config['stop_on_frame']
                self.history_frames  = self.config['history_frames']
                self.max_features    = self.registration['max_features'] 
                self.match_percent   = self.registration['good_match_percent']
            except yaml.YAMLError as exc:
                print(exc)
                return
