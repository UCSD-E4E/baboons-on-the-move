#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from pathlib import Path  # I highly encourage this library over os.path.join!
from sklearn.cluster import KMeans
import numpy as np
import math
import pickle


# ## Hyper Parameters

num_clusters = 5


# # Paths

# (should change these to the configs in the yaml later on)
root = Path("../../../")
input_velocities_csv = root / "ml_data" / "DJI_0769_1st_2250_frames.csv"


# # Get the csv into a dataframe

# In[6]:


velocities_df = pd.read_csv(input_velocities_csv)
total_num_of_baboons = velocities_df.loc[velocities_df.shape[0] - 1, "baboon id"]


# ## Gets rid of the initial frames with a Nan value. Can skip this when the script is fixed

# In[7]:


# until velocity code is fixed as to not store nan values


velocities_df = velocities_df.dropna()

# sanity check bc df's are busted
for idx, row in velocities_df.iterrows():
    if math.isnan(row.loc["velocity"]):
        print(row.loc["velocity"])
        velocities_df = velocities_df.drop(velocities_df.index[idx])


# ## Get velocities in np array

# In[8]:


velocities_series = velocities_df.loc[:, "velocity"]
velocities = velocities_series.to_numpy()


# ## Take out non moving velocities

# In[9]:


velocities = velocities[velocities != 0]


# ## Fit the Kmeans model

# In[10]:


kmeans_model = KMeans(n_clusters=num_clusters, random_state=0).fit(
    velocities.reshape(-1, 1)
)
kmeans_model.cluster_centers_  # should be the average of the cluster since it's a 1d model


# In[11]:


pickle.dump(kmeans_model, open(root / "ml_data" / "velocity_model.pkl", "wb"))


# In[ ]:
