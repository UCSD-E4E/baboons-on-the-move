import os
import shutil
from typing import Callable, Dict, List, Tuple

import cv2

from baboon_tracking.models.frame import Frame
from bom_pipeline.decorators import runtime_config
from bom_pipeline.stage_result import StageResult


def save_img_result(function: Callable):
    prev_execute = function.execute
    save = True
    frame_attributes = []
    created_folders = False

    def set_runtime_config(_, rconfig: Dict[str, any]):
        nonlocal save

        if "save" in rconfig:
            save = rconfig["save"]

    def execute(self) -> StageResult:
        nonlocal frame_attributes
        nonlocal created_folders
        result = prev_execute(self)

        if save:
            if not frame_attributes:
                frame_attributes = [
                    a for a in dir(self) if isinstance(getattr(self, a), (Frame, list))
                ]

            for frame_attribute in frame_attributes:
                frame = getattr(self, frame_attribute)
                parent_folder = f"./output/imgs/{type(self).__name__}/{frame_attribute}"
                framewrite(parent_folder, frame)

            created_folders = True

        return result

    def isinstance_list(instance: any, class_or_tuple: type or Tuple):
        if isinstance(instance, list):
            return all(isinstance(i, class_or_tuple) for i in instance)

        return False

    def framewrite(parent_folder: str, frame: Frame or List[Frame]):
        if isinstance(frame, Frame):
            framewrite_img(parent_folder, frame)
        else:
            framewrite_list(parent_folder, frame)

    def framewrite_list(parent_folder: str, frames: List[Frame]):
        if not isinstance_list(frames, Frame):
            return

        for i, frame in enumerate(frames):
            framewrite_img(f"{parent_folder}/{i}", frame)

    def framewrite_img(parent_folder: str, frame: Frame):
        if not created_folders:
            if os.path.exists(parent_folder):
                shutil.rmtree(parent_folder)
            os.makedirs(parent_folder)

        frame_number = frame.get_frame_number()
        frame_img = frame.get_frame()

        file_name = f"{parent_folder}/{frame_number:06}.jpg"
        cv2.imwrite(file_name, frame_img)

    function.execute = execute

    function.save_result_set_runtime_config = set_runtime_config

    function = runtime_config("save_result_set_runtime_config", is_property=True)(
        function
    )

    return function
