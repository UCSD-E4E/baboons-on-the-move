from abc import ABC, abstractmethod
import cv2
import numpy as np
import math
import cmath

from collections import deque
from ..models import Frame


class Registration(ABC):
    def __init__(self, history_frame_count, max_features, good_match_percent):
        self.MAX_FEATURES = max_features
        self.GOOD_MATCH_PERCENT = good_match_percent
        self.history_frame_count = history_frame_count
        self.history_frames = deque([])

    def _shift_frame(self, frames):  # , frame, previous_frame):
        """
        Takes in transformation matrix; does homography transformation to register/align two frames
        """
        frame: Frame = frames[0]
        previous_frame: Frame = frames[1]

        M = self.register(previous_frame, frame)
        # return (previous_frame, M)
        return (
            Frame(
                cv2.warpPerspective(
                    previous_frame.get_frame(),
                    M,
                    (
                        previous_frame.get_frame().shape[1],
                        previous_frame.get_frame().shape[0],
                    ),
                ).astype(np.uint8),
                previous_frame.get_frame_number(),
            ),
            M,
        )

    @abstractmethod
    def register(self, frame1: Frame, frame2: Frame):
        pass

    def is_history_frames_full(self):
        return len(self.history_frames) >= self.history_frame_count

    def push_history_frame(self, frame: Frame):
        """Adds most recent frame into history_frames, and if history_frames exceeds history_frame_count, remove the oldest frame

        Args:
            frame: grayscale opencv image frame
        """
        popped_frame = None
        if self.is_history_frames_full():
            popped_frame = self.history_frames.popleft()

        self.history_frames.append(frame)

        return popped_frame

    def shift_all_frames(self, target_frame: Frame):
        """
        Shifts all frames to target frame, returns list of shifted frames
        """
        frames = self.history_frames

        return [self._shift_frame((target_frame, f)) for f in frames]
