import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
import numpy as np
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as func
import torch.nn.init as torch_init
import torch.optim as optim
import pandas as pd
import os

"""
The Dataset Loader class for pytorch training purposes

Not really needed at the moment but will be nice to have in the future

Parameters:
    Data : should be a (n x d) np array 
"""


class loader(Dataset):
    def __init__(self, data, labels):
        if not isinstance(data, (np.ndarray)):
            raise ValueError("Data should be a numpy array")
        self.data = data
        self.labels = labels

    def __len__(self):
        return self.data.shape[0]

    # allow us to use the index for an instance of loader
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]


class Nnet(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(Nnet, self).__init__()
        # TODO: Add dropout! When we do we MUST use model.eval() for val or testing and model.train() for training
        self.input_layer = nn.Sequential(
            nn.Linear(input_dim, 500), nn.ReLU(inplace=True)
        )

        self.main = nn.Sequential(
            nn.Linear(500, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 25088),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(25088, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 500),
            nn.ReLU(inplace=True),
            nn.Dropout(),
        )

        self.output = nn.Linear(500, output_dim)

    def forward(self, input):
        x = self.input_layer(input)
        x = self.main(x)
        x = self.output(x)
        return x
