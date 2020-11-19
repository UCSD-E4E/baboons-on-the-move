import cv2
import os
from baboon_tracking.mixins.capture_mixin import CaptureMixin
from baboon_tracking.models.frame import Frame
from baboon_tracking.stages.show_last_frame import ShowLastFrame

from pipeline import Stage
from pipeline.decorators import last_stage, stage
from pipeline.stage_result import StageResult


@stage("capture")
@last_stage("dependent")
class SaveVideo(ShowLastFrame):
    def __init__(self, dependent: any, capture: CaptureMixin) -> None:
        ShowLastFrame.__init__(self, dependent)
        self._capture = capture

        self._frame_video_writers = None

    def execute(self) -> StageResult:
        ShowLastFrame.execute(self)

        # This searches the previous object for frame types.
        if not self._frame_video_writers:
            self._frame_video_writers = {
                f: cv2.VideoWriter(
                    "./output/{stage_name}.{frame_attribute}.mp4".format(
                        stage_name=type(self._dependent).__name__, frame_attribute=f,
                    ),
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    self._capture.fps,
                    (self._capture.frame_width, self._capture.frame_height),
                )
                for f in self._frame_attributes
            }

        # Write one frame to the video for each frame object.
        for frame_attribute in self._frame_attributes:
            frame = getattr(self._dependent, frame_attribute).get_frame()
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            self._frame_video_writers[frame_attribute].write(frame)

        return StageResult(True, True)

    def on_destroy(self) -> None:
        for frame_attribute in self._frame_attributes:
            self._frame_video_writers[frame_attribute].release()
