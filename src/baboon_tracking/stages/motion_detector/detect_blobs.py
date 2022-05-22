"""
Detect blobs using the built in OpenCV blob detector.
"""
import cv2
from baboon_tracking.decorators.debug import debug
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.baboon import Baboon

from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@debug(MovingForegroundMixin, (0, 255, 0))
@debug(FrameMixin, (0, 255, 0))
@stage("moving_foreground")
class DetectBlobs(Stage, BaboonsMixin):
    """
    Detect blobs using the built in OpenCV blob detector.
    """

    def __init__(
        self,
        moving_foreground: MovingForegroundMixin,
    ) -> None:
        BaboonsMixin.__init__(self)

        self._moving_foregrouned = moving_foreground

        Stage.__init__(self)

    def execute(self) -> StageResult:
        """
        Detect and returns locations of blobs from foreground mask
        Returns list of coordinates
        """

        foreground_mask = self._moving_foregrouned.moving_foreground.get_frame()

        contours, _ = cv2.findContours(
            foreground_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        rectangles = [cv2.boundingRect(c) for c in contours]
        rectangles = [(r[0], r[1], r[0] + r[2], r[1] + r[3]) for r in rectangles]

        self.baboons = [Baboon(r) for r in rectangles]
        return StageResult(True, True)
