class CaptureMixin:
    def __init__(self):
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        self.frame_count = 0

    def get_video_length(self):
        return self.frame_count / self.fps
