class Frame:
    def __init__(self, frame, frame_number):
        self._frame = frame
        self._frame_number = frame_number

    def get_frame(self):
        return self._frame

    def get_frame_number(self):
        return self._frame_number
