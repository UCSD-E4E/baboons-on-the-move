import code
import numpy as np
import ntpath
from pathlib import Path
import os
import torch
from baseline_model import * 
from particle import Particle_Filter 
import pandas as pd

"""
Given a csv of the video containing positional and direction velocity data, predicts locations of baboons 
using a particle filter
"""

root_path = Path('./../../..')

config = {}
config['model'] = root_path / 'baboon_tracking' / 'models' / 'particle_filter' / 'net.pth'
config['input_dim'] = 9
config['output_dim'] = -1 
config['kmeans_model_path'] = root_path / 'ml_data' / 'velocity_model.pkl'
config['input_csv'] = root_path / 'ml_data' / 'input_mp4.csv'
config['video_csv'] = root_path / 'ml_data' / '4_22_2020_mask.mp4_blobdetector.csv'

########## csv Initialization ##########
data = pd.read_csv(config['input_csv'])
data = pd.read_csv(config['video_csv'])


########## KMEANS Initialization ##########
kmeans = pickle.load(open(config['kmeans_model_path'], 'rb'))
kmeans_centers_sorted = np.sort(np.array(kmeans.cluster_centers_).squeeze())
config['output_dimension'] = kmeans_centers_sorted.size + 1

########## MODEL Initialization ##########
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
state_dict = torch.load(config['model'])
net.load_state_dict(state_dict)


########## PARTICLE Initialization ##########
initial_state = [2,3]
particle_filter = Particle_Filter(initial_state, kmeans_centers_sorted, config['input_dim'], config['output_dim'], net)

# frame - pass in all coordinates of blob detected baboons for the current frame (nx2)
#threshold - pixel distance from the previous position that points should be considered from the blob detector
# alpha - degree of trust in blob detector (0.8-0.9)
particle_filter.update(frame, threshold, 0.8)





