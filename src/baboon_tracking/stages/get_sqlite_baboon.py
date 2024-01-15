"""
Gets regions from a Sqlite database.
"""

from sqlite3 import connect

import numpy as np

from baboon_tracking.decorators.debug import debug
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from baboon_tracking.mixins.transformation_matrices_mixin import (
    TransformationMatricesMixin,
)
from baboon_tracking.models.region import Region
from bom_pipeline import Stage
from bom_pipeline.decorators import stage
from bom_pipeline.stage_result import StageResult


@debug(FrameMixin, (0, 255, 0))
@stage("frame")
class GetSqliteBaboon(Stage, BaboonsMixin, TransformationMatricesMixin):
    """
    Gets regions from a Sqlite database.
    """

    def __init__(self, frame: FrameMixin) -> None:
        Stage.__init__(self)
        BaboonsMixin.__init__(self)
        TransformationMatricesMixin.__init__(self)

        self._frame = frame

        self._connection = None
        self._cursor = None

    def on_init(self) -> None:
        file_name = "./output/results.db"

        if self._connection is None:
            self._connection = connect(file_name)
            self._cursor = self._connection.cursor()

    def execute(self) -> StageResult:
        frame = self._frame.frame.get_frame_number()
        regions = list(
            self._cursor.execute(
                "SELECT x1, y1, x2, y2 FROM motion_regions WHERE frame = ?", (frame,)
            )
        )
        matrix_results = list(
            self._cursor.execute(
                """
                SELECT  t11, t12, t13,
                        t21, t22, t23,
                        t31, t32, t33
                FROM transformations WHERE frame = ?
                """,
                (frame,),
            )
        )

        if regions and matrix_results:
            self.baboons = [Region(r) for r in regions]
            t11, t12, t13, t21, t22, t23, t31, t32, t33 = matrix_results[0]
            self.current_frame_transformation = np.array(
                [[t11, t12, t13], [t21, t22, t23], [t31, t32, t33]]
            )

            result = StageResult(True, True)
        else:
            result = StageResult(True, False)

        return result
