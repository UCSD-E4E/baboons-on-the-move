"""
Displays the frame within a window for the user to see.
Automatically sizes the window to the user's screen.
"""
import tkinter as tk
import cv2

from pipeline import Stage
from pipeline.decorators import last_stage
from baboon_tracking.models.frame import Frame


@last_stage("dependent")
class ShowLastFrame(Stage):
    """
    Displays the frame within a window for the user to see.
    Automatically sizes the window to the user's screen.
    """

    def __init__(self, dependent: any):
        Stage.__init__(self)

        root = tk.Tk()

        scale = 0.85

        width = int(root.winfo_screenwidth() * scale)
        height = int(root.winfo_screenheight() * scale)

        self.im_size = (width, height)

        self._dependent = dependent

        self._frame_attributes = None

    def execute(self) -> bool:
        """
        Displays the frame within a window for the user to see.
        Automatically sizes the window to the user's screen.
        """

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
                    getattr(self._dependent, frame_attribute).get_frame(), self.im_size
                ),
            )

        return True
