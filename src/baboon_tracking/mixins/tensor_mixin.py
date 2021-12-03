import torch

class TensorMixin:
    def __init__(self):
        self.tensor: torch.Tensor = None