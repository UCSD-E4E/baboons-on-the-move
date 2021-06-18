import tkinter as tk
from tkinter import ttk
import time
import datetime
from typing import Callable


class Progress:
    def __init__(self, root: tk.Tk, callback: Callable):
        progress_window = tk.Toplevel(root)
        progress_window.protocol("WM_DELETE_WINDOW", callback)
        progress_window.title("Processing Progress")
        progress_window.grab_set()

        time_remaining_label = ttk.Label(progress_window, text="Time Remaining")
        time_remaining_label.grid(column=0, row=0)

        total_time_label = ttk.Label(progress_window, text="Total Time")
        total_time_label.grid(column=0, row=1)

        time_per_iteration_label = ttk.Label(progress_window, text="Time Per Iteration")
        time_per_iteration_label.grid(column=0, row=2)

        progress_bar = ttk.Progressbar(progress_window, length=400)
        progress_bar.grid(column=0, row=3)

        self._time_remaining_label = time_remaining_label
        self._total_time_label = total_time_label
        self._time_per_iteration_label = time_per_iteration_label

        self._progress_window = progress_window
        self._progress_bar = progress_bar

        self.maximum = None
        self._start_time = None

        self._root = root

    def set_maximum(self, maximum: int):
        self.maximum = maximum
        self._progress_bar.config(mode="determinate", maximum=maximum)

    def set_value(self, value: int):
        if not self._start_time:
            self._start_time = time.perf_counter()

        self._progress_bar.config(mode="determinate", value=value, maximum=self.maximum)

        time_taken = time.perf_counter() - self._start_time

        time_per_iteration = float(time_taken) / float(value)
        total_time = self.maximum * time_per_iteration
        time_remaining = total_time - time_taken

        self._time_remaining_label.config(
            text="Time Remaining: {time_remaining}".format(
                time_remaining=str(datetime.timedelta(seconds=time_remaining))
            )
        )

        self._total_time_label.config(
            text="Total Time: {total_time}".format(
                total_time=str(datetime.timedelta(seconds=total_time))
            )
        )

        self._time_per_iteration_label.config(
            text="Time Per Iteration: {time_per_iteration}".format(
                time_per_iteration=str(datetime.timedelta(seconds=time_per_iteration))
            )
        )

    def close(self):
        self._progress_window.grab_release()
        self._progress_window.destroy()

