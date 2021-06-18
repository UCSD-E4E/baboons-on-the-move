import tkinter as tk
from tkinter import filedialog
from threading import Thread

from baboon_tracking.baboon_tracker import BaboonTracker
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from gui.progress import Progress


class App:
    def __init__(self):
        self._root = tk.Tk()
        self._continue_worker = True
        self._worker = None
        self._progress = None

    def _exit(self):
        self._root.destroy()

    def _do_work(self, name: str):
        runtime_config = {"display": False, "save": False}

        baboon_tracker = BaboonTracker(input_file=name, runtime_config=runtime_config)
        capture_mixin: CaptureMixin = baboon_tracker.get(CaptureMixin)
        frame_mixin: FrameMixin = baboon_tracker.get(FrameMixin)

        self._progress.set_maximum(capture_mixin.frame_count)

        should_continue = True
        while should_continue and self._continue_worker:
            should_continue = baboon_tracker.step().continue_pipeline

            if self._continue_worker:
                self._progress.set_value(frame_mixin.frame.get_frame_number())

        self._progress.close()

    def _close_progress(self):
        self._continue_worker = False

    def _open_file(self):
        with filedialog.askopenfile(mode="r", filetypes=[("All Videos", ".mp4")]) as f:
            self._continue_worker = True
            self._worker = Thread(target=lambda: self._do_work(f.name))
            self._worker.start()

        self._progress = Progress(self._root, self._close_progress)

    def start(self):
        root = self._root
        root.title("Engineers for Exploration Baboon Tracker")

        menu = tk.Menu(root)

        file_menu = tk.Menu(menu)
        file_menu.add_command(
            label="Open File...", underline=5, command=self._open_file
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", underline=1, command=self._exit)
        menu.add_cascade(label="File", menu=file_menu, underline=0)

        root.config(menu=menu)
        root.mainloop()

        if self._worker:
            self._continue_worker = False
