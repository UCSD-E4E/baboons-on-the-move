# import tkinter as tk
# from tkinter import filedialog
# from threading import Thread

# from baboon_tracking.baboon_tracker import BaboonTracker
# from baboon_tracking.mixins.frame_mixin import FrameMixin
# from baboon_tracking.mixins.capture_mixin import CaptureMixin
# from gui.progress import Progress

import kivy

kivy.require("2.0.0")

from kivy.app import App
from kivy.lang import Builder

from gui.main_screen import MainScreen


class BaboonTrackingApp(App):
    def __init__(self):
        App.__init__(self)

    def on_stop(self):
        MainScreen.continue_worker = False

    def build(self):
        Builder.load_file("./src/gui/app.kv")

        return MainScreen()
