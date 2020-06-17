import numpy as np
from baseline_model import *
import torch
import torch.nn as nn
import math

"""
Class for Particle filter

Terms:
    s : number of velocities
    n : number of particles

Instance Variables : 
    cluster_centers : the velocity at the center of each state (cluster centers from kmeans model)
    direction_vector : the direction vector from the previous position
    input_dim : dimension of input into model. Must be sorted
    estimated_location : (x, y) estimated location at the end of an iteration of the particle filter
    estimated_velocity : the estimated velocity at the end of an iteratin of the particle fitler
    velocities (type : np of floats, shape : n x 1) : the velocities of the n particles 
    weights (type : np of floats, shape : n x 1) : the current weights of each particle
    model (type : torch nn.Module, output_dim : s)
"""


"""
Instantiation Parameters:
    init_velocities : the initial velocities of the n particles
    direction_vector : the initial direction vector
    input_dim : dimension of input into model
    d_historic : represents the number of velocities that we consider for the motion model
    num_velocities : the number of possible velocities
    weight_distribution : the initial distribution of the weights (default : uniform)
    model : motion model 

"""
#need to add direction!!
class Particle_Filter():
    def __init__(self, init_velocities, direction_vector, estimated_location, estimated_velocity, d_historic,  cluster_centers, input_dim, model, weight_distribution='uniform'):
        # velocities
        if len(init_velocities[init_velocities < 0]) > 0:
            assert RuntimeError('Some velocities are representing a velocity that is negative')
        self.velocities = np.array(init_velocities)

        # estimated location of baboon at initialization
        self.estimated_location = estimated_location

        self.estimated_velocity = estimated_velocity

        # cluster centers
        self.cluster_centers = [0]
        self.cluster_centers.extend(cluster_centers)

        # input_dim
        self.input_dim = input_dim

        #direction vector
        self.direction_vector = direction_vector

        # model
        if not isinstance(model, Nnet):
            assert RuntimeError('The model is not of type baseline_model.Nnet')
        self.model = model

        # weight_distribution
        if weight_distribution == 'uniform':
            self.weights = np.ones(self.velocities.size) * (1/self.velocities.size)
        else:
            assert RuntimeError('Not yet implemented')


def predict(self, neighbors_and_historic):
    # input is a matrix of dimension (n x input_dim)
    model_input = np.zeros(self.velocities.size, self.input_dim)
    model_input[:][0] = self.velocities
    model_input[:][1:] = neighbors_and_historic

    # TODO : make Sure to confirm that the output is N x output_dim
    softmax_layer = nn.Softmax(dim=1)  # need this since CEL in training techincally does it for us
    model_output = self.model(model_input)
    model_output = softmax_layer(model_output).cpu().data.numpy().squeeze()

    # upate the velocities
    # self.velocities = np.array( [self.cluster_centers[pred_idx] for pred_idx in np.argmax(model_output, axis=0) ])

    # update the weights
    new_weights = []
    new_velocities = []

    for previous_weight_idx, previous_weight in enumerate(self.weights):

        current_weights = previous_weight * model_output[previous_weight_idx]  # the new weights for new particles
        # TODO : do a gaussian sampling around self.cluster_centers[pred_idx]
        current_velocities = self.cluster_centers  # the new velocities for each newly created particle above

        new_weights.extend(current_weights)
        new_velocities.extend(current_velocities)

    self.weights = new_weights
    self.velocities = new_velocities

    #frame - n x 2 matrix of all blob detected centroids in the current frame
    #threshold - pixel distance from the previous position that points should be considered from the blob detector
    #alpha - degree of trust in blob detector (probably 0.8-0.9)
    #noise - Standard Deviation = this many pixels
    #FPS - frames per second of video
    def update( self, frame, threshold, alpha=0.8, noise=8, FPS=30 ):
        predict_velocities = self.velocities
        predict_weights = self.weights
        prev_position = self.estimated_location
        prev_velocity = self.estimated_velocity
        new_velocities = []
        new_weights = []
        
        #convert velocity from predict into coordinate
        particle_cord = predict_velocities.T * direction_vector + prev_position
        
        #get all blobs within threshold range
        euclidian_distances = np.sqrt( np.square(frame[['x']]-prev_position[0][0])['x'] + np.square(frame[['y']]-prev_position[0][1])['y'] )
        nearest_blobs = frame[euclidian_distances < threshold]
        
        #if there are no nearby blobs, exit update
        if nearest_blobs.shape == (0,1):
            return
        
        #if there is a single blob nearby
        elif nearest_blobs.shape[0] == 1:
            nearest_blobs = np.full(particle_cord.shape, nearest_blobs)
        
        #if there are multiple blobs nearby, pick the best one by closest distance
        else:
            best_blob = np.zeros(particle_cord.shape)
            best_dist = np.full((particle_cord.shape[0],1), np.Infinity)
            for i, blob in nearest_blobs.iterrows():
                dist = np.sqrt( np.square(np.full((particle_cord.shape[0]),blob[0])-particle_cord[:,0]) + np.square(np.full((particle_cord.shape[0]),blob[1])-particle_cord[:,1]))
                dist = np.array([dist]).T
                best_blob[np.squeeze([dist < best_dist]),:] = blob
                best_dist[dist < best_dist] = dist[dist < best_dist]
            nearest_blobs = best_blob
            
        nearest_blobs = pd.DataFrame(data=nearest_blobs, columns=["x", "y"])
            
        
        #update coordinates for each particle & blob
        #updated coordinate = (blobs + normalized random values * 0.8) + (predicted coordinates * 0.2)
        updated_cord = (nearest_blobs+np.random.standard_normal(nearest_blobs.shape)*noise)*alpha + particle_cord*(1-alpha)
            
        #Calculate velocity for new coordinate
        new_dist = np.sqrt( np.square(updated_cord[['x']]-prev_position[0][0])['x'] + np.square(updated_cord[['y']]-prev_position[0][1])['y'] )
        new_velocities.append(new_dist/FPS)
        blob_dist = np.sqrt( np.square(updated_cord[['x']]-nearest_blobs[['x']])['x'] + np.square(updated_cord[['y']]-nearest_blobs[['y']])['y'] )
        new_weights = (max(blob_dist)-blob_dist)/max(blob_dist)*alpha+(predict_weights.squeeze()*(1-alpha))
        new_weights = new_weights/sum(new_weights)

        self.velocities = np.array(new_velocities)
        self.weights = np.array(new_weights)





