"""
Displays the frame within a window for the user to see.
Automatically sizes the window to the user's screen.
"""
from typing import Dict, Tuple
import tkinter as tk
import cv2

from pipeline import Stage


class ShowFrame(Stage):
    """
    Displays the frame within a window for the user to see.
    Automatically sizes the window to the user's screen.
    """

    def __init__(self, window_title: str, image_key: str):
        root = tk.Tk()

        scale = 0.85

        width = int(root.winfo_screenwidth() * scale)
        height = int(root.winfo_screenheight() * scale)

        self.im_size = (width, height)

        self._window_title = window_title
        self._image_key = image_key

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Displays the frame within a window for the user to see.
        Automatically sizes the window to the user's screen.
        """

        cv2.imshow(
            self._window_title,
            cv2.resize(state[self._image_key].get_frame(), self.im_size),
        )

        return (True, state)
