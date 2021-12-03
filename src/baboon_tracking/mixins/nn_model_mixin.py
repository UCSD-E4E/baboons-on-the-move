import torch
from torch import nn

class NNModelMixin:
    def __init__(self, device: torch.device, model: nn.Module):
        self.device = device
        self.model = model