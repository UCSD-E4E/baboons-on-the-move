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
    input_dim : dimension of input into model
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
    def __init__(self, init_states, input_dim, num_states, model, weight_distribution='uniform'):

        #init_states
        if len(init_states[init_states < 0]) > 0:
            assert RuntimeError('Some states are representing a velocity that is negative')
        self.states = np.array(init_states)

        #input_dim
        self.input_dim = input_dim

        #num_states
        if num_states < 2:
            assert RuntimeError('need more than one state')
        self.num_states = num_states

        #model
        if not isinstance(model, Nnet):
            assert RuntimeError('The model is not of type baseline_model.Nnet')
        self.model = model

        #weight_distribution
        if weight_distribution == 'uniform':
            self.weights = np.ones(self.states.size) * (1/self.states.size)
        else:
            assert RuntimeError('Not yet implemented')


def predict(self):
    #input is a matrix of dimension (n x input_dim)
    model_input = np.zeros(self.init_states.size, self.input_dim)
    model_input[0][:] = self.velocities

    

