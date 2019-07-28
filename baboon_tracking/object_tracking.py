class TrackingStrategy():
    def __init__(self, config):
        self.config = config

class Kalman_TrackingStrategy(TrackingStrategy):
    def track(self):
        pass

object_tracking_strategies = {
    'kalman': Kalman_TrackingStrategy
}