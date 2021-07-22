import cv2
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.models.frame import Frame

from pipeline import Stage
from pipeline.decorators import stage, config
from pipeline.stage_result import StageResult


@show_result
@config("h", "preprocess/preprocess_color/denoise_color/h")
@config("h_color", "preprocess/preprocess_color/denoise_color/h_color")
@config(
    "template_window_size",
    "preprocess/preprocess_color/denoise_color/template_window_size",
)
@config(
    "search_window_size", "preprocess/preprocess_color/denoise_color/search_window_size"
)
@stage("frame")
class DenoiseColor(Stage, FrameMixin):
    def __init__(
        self,
        h: float,
        h_color: float,
        template_window_size: int,
        search_window_size: int,
        frame: FrameMixin,
    ) -> None:
        Stage.__init__(self)
        FrameMixin.__init__(self)

        self._h = h
        self._h_color = h_color
        self._template_window_size = template_window_size
        self._search_window_size = search_window_size

        self._frame = frame

    def execute(self) -> StageResult:
        dst = cv2.fastNlMeansDenoisingColored(
            self._frame.frame.get_frame(),
            None,
            self._h,
            self._h_color,
            self._template_window_size,
            self._search_window_size,
        )

        self.frame = Frame(dst, self._frame.frame.get_frame_number())

        return StageResult(True, True)

