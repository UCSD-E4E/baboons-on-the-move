import cv2
import numpy as np
import torch
from torch import nn
from baboon_tracking.mixins.frame_mixin import FrameMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.models.frame import Frame

from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult

class ColorSpaceTransformation(nn.Module):
    def __init__(self):
        nn.Module.__init__(self)

        self.hidden_layer = nn.Linear(3, 20)
        self.output_layer = nn.Sequential(
            nn.Linear(20, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.hidden_layer(x)
        x = self.output_layer(x)

        return x

@stage("frame_mixin")
class ConvertToColorspace(Stage, PreprocessedFrameMixin):
    def __init__(self, frame_mixin: FrameMixin) -> None:
        Stage.__init__(self)
        PreprocessedFrameMixin.__init__(self)

        self._frame_mixin = frame_mixin

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ColorSpaceTransformation().to(self.device)

    def execute(self) -> StageResult:
        frame = self._frame_mixin.frame.get_frame()
        height, width, _ = frame.shape
        frame = frame.transpose(2,0,1).reshape(3,-1).T
        frame = torch.Tensor(frame).to(self.device)

        gray_frame = self.model.forward(frame)
        gray_frame *= 255
        gray_frame = gray_frame.cpu().detach().numpy().T.reshape(height, width).astype(
            np.uint8
        )

        self.processed_frame = Frame(gray_frame, self._frame_mixin.frame.get_frame_number())

        # cv2.imshow('gray_test', gray_frame)

        return StageResult(True, True)

