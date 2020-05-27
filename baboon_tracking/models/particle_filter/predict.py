import code
import numpy as np
import argparse
import ntpath
from pathlib import Path
import os
import torch
from baboon_tracking.models.particle_filter.baseline_model import * 

root_path = Path('./../../..')

parser = argparse.ArgumentParser(description='Predicts the next state given a motion model')
parser.add_argument('--model', '-m', default=root_path / 'baboon_tracking' / 'models' / 'particle_filter' / 'net.pth')
parser.add_argument('--input_dim', '-i', default=9)
parser.add_argument('--output_dim', '-o', default=6)
args = parser.parse_args()

#checks
#check if model exists
if not os.path.isfile(args.model):
    assert RuntimeError(f'The given model {args.model} does not exist')

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
net = Nnet(args.input_dim, args.output_dim).to(computing_device)
state_dict = torch.load(args.model, map_location=computing_device)
net.load_state_dict(state_dict)

