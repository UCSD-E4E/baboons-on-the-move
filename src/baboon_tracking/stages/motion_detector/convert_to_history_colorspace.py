from collections import deque
import numpy as np
import torch
from torch import nn
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.history_frames_mixin import HistoryFramesMixin
from baboon_tracking.mixins.nn_model_mixin import NNModelMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.mixins.tensor_mixin import TensorMixin
from baboon_tracking.models.frame import Frame
from os.path import isfile

from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult

class ColorSpaceTransformation(nn.Module):
    def __init__(self):
        nn.Module.__init__(self)

        self.hidden_layer = nn.Sequential(
            nn.Linear(3, 20),
            nn.ReLU()
        )
        self.output_layer = nn.Sequential(
            nn.Linear(20, 1),
            nn.ReLU(),
            # nn.Sigmoid()
        )

    def forward(self, x):
        x = self.hidden_layer(x)
        x = self.output_layer(x)

        min_x = torch.min(x)
        max_x = torch.max(x)

        x = x / (max_x - min_x)

        return x

@show_result
@stage("history_frames_mixin")
class ConvertToHistoryColorspace(Stage, HistoryFramesMixin, PreprocessedFrameMixin, NNModelMixin, TensorMixin):
    def __init__(self, history_frames_mixin: HistoryFramesMixin) -> None:
        Stage.__init__(self)
        PreprocessedFrameMixin.__init__(self)
        HistoryFramesMixin.__init__(self, history_frames_mixin._history_frame_count, history_frames_mixin.history_frame_popped)
        TensorMixin.__init__(self)

        self._history_frames_mixin = history_frames_mixin

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = ColorSpaceTransformation().to(device)

        if isfile('./output/color_space_weights.pth'):
            model.load_state_dict(torch.load('./output/color_space_weights.pth'))

        NNModelMixin.__init__(self, device, model)

    def _get_frame(self, frame: Frame):
        frame_array = frame.get_frame()
        height, width, _ = frame_array.shape
        frame_array = frame_array.transpose(2,0,1).reshape(3,-1).T
        frame_array = torch.Tensor(frame_array).to(self.device)

        gray_frame_tensor = self.model.forward(frame_array)
        gray_frame_array = gray_frame_tensor * 255
        gray_frame_array = gray_frame_array.cpu().detach().numpy().T.reshape(height, width).astype(
            np.uint8
        )

        self.tensor = gray_frame_tensor

        return Frame(gray_frame_array, frame.get_frame_number())

    def execute(self) -> StageResult:
        color_shift = [self._get_frame(h) for h in self._history_frames_mixin.history_frames]
        self.history_frames = deque(color_shift)

        self.processed_frame = color_shift[-1]

        return StageResult(True, True)

