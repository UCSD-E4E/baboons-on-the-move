from .Tracking import Tracking


class Kalman_Tracking(Tracking):
    def track(self):
        raise NotImplementedError()
