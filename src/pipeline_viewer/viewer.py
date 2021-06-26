import tkinter as tk

from pipeline.pipeline import Pipeline


class PipelineViewer:
    def __init__(self, pipeline: Pipeline):
        self._pipeline = pipeline

    def run(self):
        root = tk.Tk()
        root.title(type(self._pipeline).__name__)

        root.mainloop()
