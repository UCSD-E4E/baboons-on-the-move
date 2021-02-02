"""
Displays the frame within a window for the user to see.
Automatically sizes the window to the user's screen.
"""
import tkinter as tk
import os
import cv2

from baboon_tracking.mixins.capture_mixin import CaptureMixin
from pipeline import Stage
from pipeline.decorators import last_stage, stage
from pipeline.stage_result import StageResult
from baboon_tracking.models.frame import Frame


@last_stage("dependent")
@stage("capture")
class ShowLastFrame(Stage):
    """
    Displays the frame within a window for the user to see.
    Automatically sizes the window to the user's screen.
    """

    def __init__(self, dependent: any, capture: CaptureMixin):
        Stage.__init__(self)

        self.im_size = None
        self._capture = capture
        self._dependent = dependent

        self._frame_attributes = None

    def execute(self) -> StageResult:
        """
        Displays the frame within a window for the user to see.
        Automatically sizes the window to the user's screen.
        """

        if self.im_size is None:
            scale = 0.85

            width = os.getenv("WIDTH")
            height = os.getenv("HEIGHT")

            if not width or not height:
                if os.environ.get("DISPLAY", "") == "":
                    width = 0
                    height = 0
                else:
                    root = tk.Tk()

                    width = root.winfo_screenwidth()
                    height = root.winfo_screenheight()

            width = int(width)
            height = int(height)

            width_scale = width / self._capture.frame_width
            height_scale = height / self._capture.frame_height

            if width_scale < height_scale:
                height = self._capture.frame_height * width_scale
            else:
                width = self._capture.frame_width * height_scale

            width = int(width * scale)
            height = int(height * scale)

            self.im_size = (width, height)

        if os.environ.get("DISPLAY", "") != "":
            # This searches the previous object for frame types.
            if not self._frame_attributes:
                self._frame_attributes = [
                    a
                    for a in dir(self._dependent)
                    if isinstance(getattr(self._dependent, a), Frame)
                ]

            # Display one cv2.imshow for each frame object.
            for frame_attribute in self._frame_attributes:
                cv2.imshow(
                    "{stage_name}.{frame_attribute}".format(
                        stage_name=type(self._dependent).__name__,
                        frame_attribute=frame_attribute,
                    ),
                    cv2.resize(
                        getattr(self._dependent, frame_attribute).get_frame(),
                        self.im_size,
                    ),
                )

        return StageResult(True, True)
