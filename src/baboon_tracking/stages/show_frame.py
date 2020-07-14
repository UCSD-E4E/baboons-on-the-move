import cv2
import tkinter as tk

from typing import Dict, Tuple
from ...pipeline import Stage


class ShowFrame(Stage):
    def __init__(self, window_title: str, image_key: str):
        root = tk.Tk()

        scale = 0.85

        width = int(root.winfo_screenwidth() * scale)
        height = int(root.winfo_screenheight() * scale)

        self.im_size = (width, height)

        self._window_title = window_title
        self._image_key = image_key

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        cv2.imshow(self._window_title, cv2.resize(state[self._image_key], self.im_size))

        return (True, state)
