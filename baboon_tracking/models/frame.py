class Frame:
    def __init__(self, frame, frame_number):
        self._frame = frame
        self._frame_number = frame_number

    def get_frame(self):
        return self._frame

    def set_frame(self, new_frame):
        self._frame = new_frame

    def get_frame_number(self):
        return self._frame_number

    def __hash__(self):
        return self.get_frame_number()
