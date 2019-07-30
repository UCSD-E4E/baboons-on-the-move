from .interface import TrackingStrategy

class Kalman_TrackingStrategy(TrackingStrategy):
    def track(self):
        raise NotImplementedError()
