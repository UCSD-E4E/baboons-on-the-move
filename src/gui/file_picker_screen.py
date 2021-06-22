from typing import Callable
from kivy.uix.popup import Popup


class FilePickerScreen(Popup):
    def __init__(self, default_path):
        self.default_path = default_path
        self._callback = None

        Popup.__init__(self)

    def cancel(self):
        self.dismiss()

        self._callback(None, None)

    def load(self, path, selection):
        self.dismiss()

        self._callback(path, selection)

    def show(self, callback: Callable):
        self._callback = callback

        self.open()
