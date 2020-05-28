import code
import numpy as np
import ntpath
from pathlib import Path
import os
import torch
from baseline_model import * 

root_path = Path('./../../..')

config = {}
config['model'] = root_path / 'baboon_tracking' / 'models' / 'particle_filter' / 'net.pth'
config['input_dim'] = 9
config['output_dim'] = 6

########## COPY THE BELOW CODE TO THE TOP OF THE FILE WHEN MERGING PARTICLE FILTER CODE ##########
# Setup GPU optimization if CUDA is supported
use_cuda = torch.cuda.is_available()
if use_cuda:
    computing_device = torch.device("cuda")
    extras = {"num_workers": 1, "pin_memory": True}
    print("CUDA is supported")
else: # Otherwise, train on the CPU
    computing_device = torch.device("cpu")
    extras = False
    print("CUDA NOT supported")
    
# Initialize network
net = Nnet(config['input_dim'], config['output_dim']).to(computing_device)
state_dict = torch.load(config['model'], map_location=computing_device)
net.load_state_dict(state_dict)

########## COPY THE ABOVE CODE TO THE TOP OF THE FILE WHEN MERGING PARTICLE FILTER CODE ##########


def predict(weights, net):
    pass






