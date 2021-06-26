from numpy.core.records import array
from sklearn.mixture import BayesianGaussianMixture

import numpy as np
import pickle

sample = np.random.rand(6, 6)

csv_reader = np.loadtxt(
    open("ml_data/input_mp4.csv"), delimiter=",", skiprows=1, usecols=[0, 2, 3]
)
x = list(csv_reader)
position_data = np.array(x).astype("float")
total_displacements = len(position_data) - 112
disp_data = [0] * total_displacements


rows = 0
disp_row = 0
baboon = 0

while rows < total_displacements - 1:
    rows += 1
    current_baboon = position_data[rows, 0]

    if baboon == current_baboon:
        x_disp = position_data[rows, 1] - position_data[rows - 1, 1]
        y_disp = position_data[rows, 2] - position_data[rows - 1, 2]

        disp_data[disp_row] = np.sqrt(x_disp ** 2 + y_disp ** 2)
        disp_row += 1

    elif baboon != current_baboon:
        baboon += 1

""""
Debugging Code:
​
print(disp_data)
print(current_baboon)
print(baboon)
print(len(position_data))
print(len(disp_data))
"""
disp_data = np.array(disp_data)
disp_data = disp_data.reshape(-1, 1)

bayesian_model = BayesianGaussianMixture(
    n_components=5,
    covariance_type="full",
    weight_concentration_prior_type="dirichlet_process",
    max_iter=100,
    init_params="random",
).fit(disp_data)

with open("displacement_mixture.pickle", "wb") as f:
    pickle.dump(bayesian_model, f)


# print(bayesian_model)
