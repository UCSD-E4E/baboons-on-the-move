from os.path import expanduser, join
from threading import Thread
from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread

from baboon_tracking.baboon_tracker import BaboonTracker
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from gui.file_picker_screen import FilePickerScreen
from gui.progress_screen import ProgressScreen


class MainScreen(Screen):
    continue_worker = True

    def __init__(self):
        Screen.__init__(self)

        self._worker = None
        self._progress = None

    def open_file(self):
        file_picker = FilePickerScreen(expanduser("~"))
        file_picker.show(self._open_file_callback)

    def _open_file_callback(self, path, selection):
        if path is None or selection is None:
            return

        self._worker = Thread(target=lambda: self._do_work(join(path, selection[0])))
        self._worker.start()

        self._progress = ProgressScreen()
        self._progress.open()

    @mainthread
    def _close_progress(self):
        self._progress.dismiss()

    def _do_work(self, name: str):
        runtime_config = {"display": False, "save": False}

        baboon_tracker = BaboonTracker(input_file=name, runtime_config=runtime_config)
        capture_mixin: CaptureMixin = baboon_tracker.get(CaptureMixin)
        frame_mixin: FrameMixin = baboon_tracker.get(FrameMixin)

        self._progress.progress_max = capture_mixin.frame_count

        should_continue = True
        while should_continue and self.continue_worker:
            should_continue = baboon_tracker.step().continue_pipeline

            if self.continue_worker:
                self._progress.set_progress_value(frame_mixin.frame.get_frame_number())

        self._close_progress()

    def exit(self):
        self.exit()
