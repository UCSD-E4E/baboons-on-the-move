"""
Detect blobs using the built in OpenCV blob detector.
"""
import cv2
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.blob_image_mixin import BlobImageMixin
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.baboon import Baboon
from baboon_tracking.models.frame import Frame

from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@show_result
@stage("moving_foreground")
class DetectBlobs(Stage, BlobImageMixin, BaboonsMixin):
    """
    Detect blobs using the built in OpenCV blob detector.
    """

    def __init__(self, moving_foreground: MovingForegroundMixin,) -> None:
        BlobImageMixin.__init__(self)
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

        blob_image = cv2.cvtColor(foreground_mask, cv2.COLOR_GRAY2BGR)
        for rect in rectangles:
            blob_image = cv2.rectangle(
                blob_image, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2
            )

        self.blob_image = Frame(
            blob_image, self._moving_foregrouned.moving_foreground.get_frame_number(),
        )

        self.baboons = [Baboon(r) for r in rectangles]
        return StageResult(True, True)
