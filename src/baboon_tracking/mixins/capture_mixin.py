"""
Mixin for returning capture information.
"""


class CaptureMixin:
    """
    Mixin for returning capture information.
    """

    def __init__(self):
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        self.frame_count = 0
        self.name = ""

    def get_video_length(self):
        """
        Get the total length of the video.
        """
        return self.frame_count / self.fps
