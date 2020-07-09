from .runners import CheckForExitRunner, FrameDisplayRunner, VideoRunner
from ..runner import Serial


class BaboonTracker:
    def __init__(self):
        self._videoRunner = VideoRunner("./data/input.mp4")

        self._runner = Serial(
            "BaboonTracker",
            self._videoRunner,
            FrameDisplayRunner("Frame"),
            CheckForExitRunner(),
        )

    def run(self):
        while True:
            success, _ = self._runner.execute(None)

            if not success:
                return

    def flowchart(self):
        img, _, _, = self._runner.flowchart()
        return img
