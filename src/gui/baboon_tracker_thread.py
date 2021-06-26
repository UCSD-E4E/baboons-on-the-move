from threading import Thread
from typing import Callable

from baboon_tracking.baboon_tracker import BaboonTracker
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.capture_mixin import CaptureMixin


class BaboonTrackerThread(Thread):
    def __init__(
        self, input_file, update_value_callback: Callable, finished_callback: Callable
    ):
        Thread.__init__(self)

        runtime_config = {"display": False, "save": False}

        self._baboon_tracker = BaboonTracker(
            input_file=input_file, runtime_config=runtime_config
        )
        self._frame: FrameMixin = self._baboon_tracker.get(FrameMixin)
        self._update_value_callback = update_value_callback
        self._finished_callback = finished_callback

        self._continue_worker = True

    def get_frame_count(self):
        capture: CaptureMixin = self._baboon_tracker.get(CaptureMixin)

        return capture.frame_count

    def run(self) -> None:
        should_continue = True
        while should_continue and self._continue_worker:
            should_continue = self._baboon_tracker.step().continue_pipeline

            if self._continue_worker:
                self._update_value_callback(self._frame.frame.get_frame_number())

        self._finished_callback()

    def abort(self):
        self._continue_worker = False
