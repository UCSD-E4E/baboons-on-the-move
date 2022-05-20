from typing import Callable, Dict, List, Tuple
from baboon_tracking.decorators.save_result import save_result
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.models.frame import Frame
from pipeline.parent_stage import ParentStage

from pipeline.stage import Stage
from pipeline.stage_result import StageResult
import cv2


@show_result
@save_result
class DisplayDebugRegions(Stage):
    stage_debug_map: Dict[Stage, List[Tuple[Stage, Tuple[int, int, int]]]] = {}

    def __init__(self):
        Stage.__init__(self)

        self._data_attribute_map = None
        self._debug_attribute_map = None

    def execute(self) -> StageResult:
        if not self._data_attribute_map:
            self._data_attribute_map = {}

            for (
                data_stage,
                debug_stage_list,
            ) in DisplayDebugRegions.stage_debug_map.items():
                self._data_attribute_map[data_stage] = [
                    a
                    for a in dir(data_stage)
                    if isinstance(getattr(data_stage, a), Frame)
                ]

                debug_stage_list.sort(key=lambda x: x[2])
                debug_stage_list.reverse()

        for data_stage, data_attributes in self._data_attribute_map.items():
            for data_attribute in data_attributes:
                frame: Frame = getattr(data_stage, data_attribute)
                debug_frame = frame.get_frame().copy()

                if len(debug_frame.shape) == 2 or debug_frame.shape[2] == 1:
                    debug_frame = cv2.cvtColor(debug_frame, cv2.COLOR_GRAY2BGR)

                debug_stage_list = DisplayDebugRegions.stage_debug_map[data_stage]

                for debug_stage, color, _ in debug_stage_list:
                    if debug_stage.baboons:
                        rectangles = [
                            (b.rectangle, b.id_str) for b in debug_stage.baboons
                        ]
                        for rect, id_str in rectangles:
                            debug_frame = cv2.rectangle(
                                debug_frame,
                                (rect[0], rect[1]),
                                (rect[2], rect[3]),
                                color,
                                2,
                            )

                            if id_str is not None:
                                cv2.putText(
                                    debug_frame,
                                    id_str,
                                    (rect[0], rect[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.9,
                                    color,
                                    2,
                                )

                setattr(
                    self, data_attribute, Frame(debug_frame, frame.get_frame_number())
                )

        return StageResult(True, True)


def debug(frame_mixin: Callable, color: Tuple[int, int, int], priority=0):
    def inner_function(function: Callable):
        prev_before_init = function.before_init
        prev_on_init = function.on_init
        most_recent_mixin = None

        def before_init(self):
            nonlocal prev_before_init
            nonlocal most_recent_mixin

            prev_before_init(self)

            most_recent_mixin = [
                s
                for s in reversed(ParentStage.static_stages)
                if isinstance(s, frame_mixin)
            ][0]

        def on_init(self):
            nonlocal prev_on_init
            prev_on_init(self)

            if most_recent_mixin not in DisplayDebugRegions.stage_debug_map:
                DisplayDebugRegions.stage_debug_map[most_recent_mixin] = []

            DisplayDebugRegions.stage_debug_map[most_recent_mixin].append(
                (self, color, priority)
            )

        function.before_init = before_init
        function.on_init = on_init

        return function

    return inner_function
