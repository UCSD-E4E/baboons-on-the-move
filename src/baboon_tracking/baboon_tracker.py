from .runners import VideoRunner
from ..runner import Serial


class BaboonTracker:
    def __init__(self):
        self._videoRunner = VideoRunner("./data/input.mp4")

        self._runner = Serial("BaboonTracker", self._videoRunner)

    def run(self):
        while True:
            self._runner.execute(None)

    def flowchart(self):
        img, _, _, = self._runner.flowchart()
        return img
