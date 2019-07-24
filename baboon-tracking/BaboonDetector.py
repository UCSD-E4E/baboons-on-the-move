from registration import REGISTRATION_STRATEGIES

class BaboonDetector():
    self.registration_strategy = None
    self.image_diff_strategy = None
    self.blob_tracking_strategy = None

    def __init__(self, configs):
        self.registration_strategy = REGISTRATION_STRATEGIES[configs['registration_strategy']]
        self.image_diff_strategy = None
        self.blob_tracking_strategy = None