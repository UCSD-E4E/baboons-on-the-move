import numpy as np
from baseline_model import *
import torch
import torch.nn as nn

"""
Class for Particle filter

Terms:
    s : number of velocities
    n : number of particles

Fields : 
    num_velocities : number of possible velocities 
    cluster_centers : the velocity at the center of each state (cluster centers from kmeans model)
    input_dim : dimension of input into model. Must be sorted
    estimated_location : the estimated location at the end of an iteration of the particle filter
    estimated_velocity : the estimated velocity at the end of an iteratin of the particle fitler
    velocities (type : list of floats, shape : n x 1) : the velocities of the n particles 
    weights (type : list of floats, shape : n x 1) : the current weights of each particle
    model (type : torch nn.Module, output_dim : s)


Parameters:
    init_velocities : the initial velocities of the n particles
    input_dim : dimension of input into model
    d_historic : represents the number of velocities that we consider for the motion model
    num_velocities : the number of possible velocities
    weight_distribution : the initial distribution of the weights (default : uniform)
    model : motion model 

"""


class Particle_Filter:
    def __init__(
        self,
        init_velocities,
        estimated_location,
        estimated_velocity,
        d_historic,
        cluster_centers,
        input_dim,
        model,
        weight_distribution="uniform",
    ):
        # velocities
        if len(init_velocities[init_velocities < 0]) > 0:
            assert RuntimeError(
                "Some velocities are representing a velocity that is negative"
            )
        self.velocities = np.array(init_velocities)

        # estimated location of baboon at initialization
        self.estimated_location = estimated_location

        self.estimated_velocity = estimated_velocity

        # cluster centers
        self.cluster_centers = [0]
        self.cluster_centers.extend(cluster_centers)

        # input_dim
        self.input_dim = input_dim

        # model
        if not isinstance(model, Nnet):
            assert RuntimeError("The model is not of type baseline_model.Nnet")
        self.model = model

        # weight_distribution
        if weight_distribution == "uniform":
            self.weights = np.ones(self.velocities.size) * (1 / self.velocities.size)
        else:
            assert RuntimeError("Not yet implemented")


def predict(self, neighbors_and_historic):
    # input is a matrix of dimension (n x input_dim)
    model_input = np.zeros(self.velocities.size, self.input_dim)
    model_input[:][0] = self.velocities
    model_input[:][1:] = neighbors_and_historic

    # TODO : make Sure to confirm that the output is N x output_dim
    softmax_layer = nn.Softmax(
        dim=1
    )  # need this since CEL in training techincally does it for us
    model_output = self.model(model_input)
    model_output = softmax_layer(model_output).cpu().data.numpy().squeeze()

    # upate the velocities
    # self.velocities = np.array( [self.cluster_centers[pred_idx] for pred_idx in np.argmax(model_output, axis=0) ])

    # update the weights
    new_weights = []
    new_velocities = []

    for previous_weight_idx, previous_weight in enumerate(self.weights):

        current_weights = (
            previous_weight * model_output[previous_weight_idx]
        )  # the new weights for new particles
        # TODO : do a gaussian sampling around self.cluster_centers[pred_idx]
        current_velocities = (
            self.cluster_centers
        )  # the new velocities for each newly created particle above

        new_weights.extend(current_weights)
        new_velocities.extend(current_velocities)

    self.weights = new_weights
    self.velocities = new_velocities
