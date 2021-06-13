from typing import Callable, Dict
import pathlib
import cv2
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.models.frame import Frame
from pipeline.decorators import runtime_config, stage

from pipeline.stage_result import StageResult


def save_result(function: Callable):
    prev_execute = function.execute
    prev_on_destroy = function.on_destroy
    save = True
    frame_video_writers = []
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
                    a for a in dir(self) if isinstance(getattr(self, a), Frame)
                ]

            if not frame_video_writers:
                frame_video_writers = {
                    f: cv2.VideoWriter(
                        "./output/{stage_name}.{frame_attribute}.mp4".format(
                            stage_name=type(self).__name__, frame_attribute=f,
                        ),
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        capture.fps,
                        (capture.frame_width, capture.frame_height),
                    )
                    for f in frame_attributes
                }

            # Write one frame to the video for each frame object.
            for frame_attribute in frame_attributes:
                frame = getattr(self, frame_attribute).get_frame()
                if len(frame.shape) == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                frame_video_writers[frame_attribute].write(frame)

        return result

    def on_destroy(self) -> None:
        prev_on_destroy(self)

        for frame_attribute in frame_attributes:
            frame_video_writers[frame_attribute].release()

    function.execute = execute
    function.on_destroy = on_destroy
    function.save_result_set_runtime_config = set_runtime_config
    function.save_result_set_capture = set_capture

    function = runtime_config("save_result_set_runtime_config", is_property=True)(
        function
    )
    function = stage("save_result_set_capture", is_property=True)(function)

    return function
