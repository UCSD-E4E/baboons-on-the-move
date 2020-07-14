from .stages import ConvertFromBGR2Gray, GetVideoFrame, ShowFrame, TestExit
from ..pipeline import Serial


class BaboonTracker:
    def __init__(self):
        self._runner = Serial(
            "BaboonTracker",
            GetVideoFrame("./data/input.mp4"),
            ShowFrame("Frame", "frame"),
            ConvertFromBGR2Gray(),
            ShowFrame("Gray", "gray"),
            TestExit(),
        )

    def run(self):
        state = {}
        while True:
            # By reusing the state, we can store state between frames.
            success, state = self._runner.execute(state)

            if not success:
                return

    def flowchart(self):
        img, _, _, = self._runner.flowchart()
        return img
