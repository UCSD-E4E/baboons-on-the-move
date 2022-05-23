"""
Provides a decorator for automatically saving the results of current stage to a video file.
"""

from ast import Tuple
from typing import Callable, Dict, List
import pathlib
import cv2
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.models.frame import Frame
from pipeline.decorators import runtime_config, stage

from pipeline.stage_result import StageResult


def save_result(function: Callable):
    """
    Provides a decorator for automatically saving the results of current stage to a video file.
    """

    prev_execute = function.execute
    prev_on_destroy = function.on_destroy
    save = True
    frame_video_writers = {}
    capture = None
    frame_attributes = []

    pathlib.Path("./output").mkdir(exist_ok=True)

    def set_runtime_config(_, rconfig: Dict[str, any]):
        nonlocal save

        if "save" in rconfig:
            save = rconfig["save"]

    def set_capture(_, cap: CaptureMixin):
        nonlocal capture
        capture = cap

    def execute(self) -> StageResult:
        nonlocal frame_video_writers
        nonlocal frame_attributes

        result = prev_execute(self)

        if save:
            if not frame_attributes:
                frame_attributes = [
                    a for a in dir(self) if isinstance(getattr(self, a), (Frame, list))
                ]

            # if not frame_video_writers:
            #     frame_video_writers = {
            #         f: cv2.VideoWriter(
            #             f"./output/{type(self).__name__}.{f}.mp4",
            #             cv2.VideoWriter_fourcc(*"mp4v"),
            #             capture.fps,
            #             (capture.frame_width, capture.frame_height),
            #         )
            #         for f in frame_attributes
            #     }

            # Write one frame to the video for each frame object.
            for frame_attribute in frame_attributes:
                frame = getattr(self, frame_attribute)
                videowrite(
                    f"{type(self).__name__}.{frame_attribute}",
                    frame,
                    frame_video_writers,
                )

        return result

    def videowrite(
        name: str,
        frame: Frame or List[Frame],
        frame_video_writers: Dict[str, cv2.VideoWriter],
    ):
        if isinstance(frame, Frame):
            videowrite_img(name, frame, frame_video_writers)
        else:
            videowrite_list(name, frame, frame_video_writers)

    def videowrite_list(
        name: str, frames: List[Frame], frame_video_writers: Dict[str, cv2.VideoWriter]
    ):
        if not isinstance_list(frames, Frame):
            return

        for i, frame in enumerate(frames):
            videowrite_img(f"{name}[{i}]", frame, frame_video_writers)

    def videowrite_img(
        name: str, frame: Frame, frame_video_writers: Dict[str, cv2.VideoWriter]
    ):
        if name not in frame_video_writers:
            frame_video_writers[name] = cv2.VideoWriter(
                f"./output/{name.replace('[', '_').replace(']', '_')}.mp4",
                cv2.VideoWriter_fourcc(*"mp4v"),
                capture.fps,
                (capture.frame_width, capture.frame_height),
            )

        frame = frame.get_frame()
        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        frame_video_writers[name].write(frame)

    def isinstance_list(instance: any, class_or_tuple: type or Tuple):
        if isinstance(instance, list):
            return all(isinstance(i, class_or_tuple) for i in instance)

        return False

    def on_destroy(self) -> None:
        prev_on_destroy(self)

        for _, frame_video_writer in frame_video_writers.items():
            frame_video_writer.release()

    function.execute = execute
    function.on_destroy = on_destroy
    function.save_result_set_runtime_config = set_runtime_config
    function.save_result_set_capture = set_capture

    function = runtime_config("save_result_set_runtime_config", is_property=True)(
        function
    )
    function = stage("save_result_set_capture", is_property=True)(function)

    return function
