from .runners import BGR2GrayRunner, CheckForExitRunner, FrameDisplayRunner, VideoRunner
from ..runner import Serial


class BaboonTracker:
    def __init__(self):
        self._runner = Serial(
            "BaboonTracker",
            VideoRunner("./data/input.mp4"),
            FrameDisplayRunner("Frame", "frame"),
            BGR2GrayRunner(),
            FrameDisplayRunner("Gray", "gray"),
            FrameDisplayRunner("Gray", "gray"),
            CheckForExitRunner(),
        )

    def run(self):
        while True:
            success, _ = self._runner.execute({})

            if not success:
                return

    def flowchart(self):
        img, _, _, = self._runner.flowchart()
        return img
