import time
import datetime
from kivy.clock import mainthread
from kivy.uix.popup import Popup
import kivy.properties as kyprops


class ProgressScreen(Popup):
    time_remaining = kyprops.NumericProperty(0)
    total_time = kyprops.NumericProperty(0)
    time_per_iteration = kyprops.NumericProperty(0)

    progress_max = kyprops.NumericProperty(0)
    _progress_value = kyprops.NumericProperty(0)

    def __init__(self):
        self._start_time = None

        Popup.__init__(self)

    @mainthread
    def set_progress_value(self, value):
        if not self._start_time:
            self._start_time = time.perf_counter()

        time_taken = time.perf_counter() - self._start_time

        self.time_per_iteration = float(time_taken) / float(value)
        self.total_time = self.progress_max * self.time_per_iteration
        self.time_remaining = self.total_time - time_taken

        self._progress_value = value

    def format_time(self, value):
        return str(datetime.timedelta(seconds=value))
