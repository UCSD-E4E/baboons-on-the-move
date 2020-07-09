from .runners import BGR2GrayRunner, CheckForExitRunner, FrameDisplayRunner, VideoRunner
from ..runner import Serial


class BaboonTracker:
    def __init__(self):
        self._videoRunner = VideoRunner("./data/input.mp4")

        self._runner = Serial(
            "BaboonTracker",
            self._videoRunner,
            FrameDisplayRunner("Frame"),
            BGR2GrayRunner(),
            FrameDisplayRunner("Gray"),
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
