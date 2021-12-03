import numpy as np
import cv2
import torch
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin

from baboon_tracking.mixins.nn_model_mixin import NNModelMixin
from baboon_tracking.mixins.preprocessed_frame_mixin import PreprocessedFrameMixin
from baboon_tracking.mixins.tensor_mixin import TensorMixin
from library.labeled_data import get_regions_from_xml
from library.region import check_if_same_region
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult
import adabound


@stage("nn_model_mixin")
@stage("tensor_mixin")
@stage("baboons_mixin")
@stage("preprocessed_frame_mixin")
class Backprop(Stage):
    def __init__(self, nn_model_mixin: NNModelMixin, tensor_mixin: TensorMixin, baboons_mixin: BaboonsMixin, preprocessed_frame_mixin: PreprocessedFrameMixin) -> None:
        Stage.__init__(self)

        self._nn_model_mixin = nn_model_mixin
        self._tensor_mixin = tensor_mixin
        self._baboons_mixin = baboons_mixin
        self._preprocessed_frame_mixin = preprocessed_frame_mixin

        self.baboon_labels = get_regions_from_xml("./data/input.xml")
        # self.optimizer = torch.optim.Adam(self._nn_model_mixin.model.parameters(), lr=1e-3)
        self.optimizer = adabound.AdaBound(self._nn_model_mixin.model.parameters(), lr=1, final_lr=1e-10)

    def execute(self) -> StageResult:
        new_found_baboons = [b.rectangle for b in self._baboons_mixin.baboons]
        labeled_baboons = self.baboon_labels[self._preprocessed_frame_mixin.processed_frame.get_frame_number()]
        error_space = []
        for new_found_baboon in new_found_baboons:
            baboon_in_labels = [
                lb
                for lb in labeled_baboons
                if check_if_same_region(lb, new_found_baboon)
            ]

            if not baboon_in_labels:
                error_space.append(new_found_baboon)

            labeled_baboons = [
                lb for lb in labeled_baboons if lb not in baboon_in_labels
            ]
        error_space.extend(labeled_baboons)
        error_mask = np.zeros_like(self._preprocessed_frame_mixin.processed_frame.get_frame())

        for rect in error_space:
            error_mask = cv2.rectangle(
                error_mask, (rect[0], rect[1]), (rect[2], rect[3]), 255, -1
            )

        error_mask = (error_mask == 255)
        height, width = error_mask.shape
        error_mask = torch.Tensor(error_mask.T.reshape(height * width)).to(self._nn_model_mixin.device)

        loss = (self._tensor_mixin.tensor + 1e5) * error_mask.unsqueeze(1)
        loss /= 1e5
        loss = torch.sigmoid(loss)
        loss = loss.sum()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        torch.save(self._nn_model_mixin.model.state_dict(), './output/color_space_weights.pth')

        return StageResult(True, True)

