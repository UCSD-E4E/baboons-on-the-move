from cv2 import ellipse
import numpy as np
from numpy.random import randint
import cv2
from sklearn.mixture import BayesianGaussianMixture
from random import random
from math import sin, cos, pi
from pickle import load

canvas = np.zeros((400, 400, 3))
# 30*30

def set_locations(num_blobs: int, background: np.array):
    """    
    takes the image values and converts them into 2d arrays
    returns random locations (x,y) as seed points for the blobs
    
    """
    
    return (x,y)

def create_blobs(
    n_blobs: int, background: np.array, locations: np.array, angles: np.array,
):
    """
    takes the number of blobs, the canvas, locations, and angles and returns ellipse frame
    with ellipses matching those parameters

    use traveled distances to create the proper ratio between length and width
    and make sure that the right most value is always the highest value and so that the baboon faces
    the right direction     

    """
        max_width = 10
        min_width = 1
        positions = np.random.randint(0, 400, size=(n_blobs, 2))

        for x, y in positions:
            axes_length = (,)
            ellipsis_frame = cv2.ellipse(
                background,
                locations,
                axes_length,
                angles,
                0,
                360,
                color=(255, 255, 255),
                thickness=-1,
            )
        

        return ellipsis_frame


        
def new_locations(model: BayesianGaussianMixture, positions):
    # takes current location of blobs and gives it a new location
    # if new_location is outside of bounds, delete that blob or create new blobs
    # include set of distance traveled and angle at the output
    """
    positions is from gaussian mixture
    angles are found by taking old and new positions and using tan
    distances is pythagorean theorem
    """

    sample, _ = model.sample()
    degs = random() * 2 * pi
    n_baboons = len(positions)


    n = 0
    while n < n_baboons:
        delta_x = int(np.asscalar(np.round(sample * sin(degs))))
        delta_y = int(np.asscalar(np.round(sample * cos(degs))))
        positions[n] = (positions[n] + delta_x, positions[n] + delta_y)
        # if position[n] is #outof bounds
        # delete it and create new random baboon location

        n += 1


    return positions, distances, angles


def pixelate(image):
    # looks for non-zero values in image and replaces them probabilistically
    # if random() < threshold value (going to experiment a bit to find how pixelated we want them)

    return image

# initialize

current_frame = 0
total_frames = 100
numblobs = 10
#film =

with open("./displacement_mixture.pickle", "rb") as f:
    model: BayesianGaussianMixture = load(f)

locations = (x,y) = set_locations(numblobs, canvas)
locations, angles= new_locations(model, locations)

# process
while(current_frame < total_frames):
    
    frame = create_blobs(canvas, locations, angles)
    frame = pixelate(frame)
    #append frame to film object
    
    if random() < .03:
        locations = np.append(locations, set_locations(1,canvas))
    if random() < .02:
        locations = np.delete(locations, 6, 0)
    
    locations = new_locations(model, numblobs)

#play film

