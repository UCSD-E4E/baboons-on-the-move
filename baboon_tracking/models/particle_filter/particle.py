import numpy as np
from baseline_model import * 
import torch

"""
Class for Particle filter

Terms:
    s : number of states
    n : number of particles

Fields : 
    num_states : number of possible states 
    cluster_centers : the velocity at the center of each state (cluster centers from kmeans model)
    input_dim : dimension of input into model. Must be sorted
    states (type : list of floats, length : n) : the states of the n particles 
    weights (type : list of floats, length : n) : the current weights of each particle
    model (type : torch nn.Module, output_dim : s)


Parameters:
    init_states : the initial velocities of the n particles
    input_dim : dimension of input into model
    num_states : the number of possible states
    weight_distribution : the initial distribution of the weights (default : uniform)
    model : motion model 

"""
class Particle_Filter():
    def __init__(self, init_states, cluster_centers, input_dim, model, weight_distribution='uniform'):

        #states
        if len(init_states[init_states < 0]) > 0:
            assert RuntimeError('Some states are representing a velocity that is negative')
        self.states = np.array(init_states)

        self.cluster_centers = cluster_centers

        #input_dim
        self.input_dim = input_dim

        #model
        if not isinstance(model, Nnet):
            assert RuntimeError('The model is not of type baseline_model.Nnet')
        self.model = model

        #weight_distribution
        if weight_distribution == 'uniform':
            self.weights = np.ones(self.states.size) * (1/self.states.size)
        else:
            assert RuntimeError('Not yet implemented')


def predict(self, neighbors_and_historic):
    #input is a matrix of dimension (n x input_dim)
    model_input = np.zeros(self.states.size, self.input_dim)
    model_input[:][0] = self.velocities
    model_input[:][1:] = neighbors_and_historic

    model_output = self.model(model_input).cpu().data.numpy().squeeze()

    #upate the velocities
    #TODO : do a gaussian sampling around self.cluster_centers[pred_idx] 
    self.states = np.array( [self.cluster_centers[pred_idx] for pred_idx in np.argmax(model_output, axis=0) ])

    #update the weights
    new_weights = np.zeros(self.states.size + (model_output.shape[1] - 1)*self.states.size, ) 
    for idx, prediction in enumerate(model_output):
        pass

    self.weights = new_weights 


    

