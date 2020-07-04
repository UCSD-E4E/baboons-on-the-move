# General Notes 
ipynb have been converted to py files so that they can be more comfortably used in the nautilus environment for training. Please convert notebooks that run on gpu hardware to python scripts

# Fully Trained Model : 

# How to Train 
1. A csv containing the velocities, centroid position, and direction of motion is always required (link above)  
3. Run the preprocess_data.py that will get the data in a format for training. More specifically findiong the nearest baboons per frame and the historic velocities for a given baboon.  Outputted data is found in this directory at data.npy and labels.npy.  
4. Train the model using the train_motion_model_kalman (CUDA enabled GPU is recommended). Model is outputted at net.pth in the current directory along with the tensorboard metrics in its own directory.  
5. Use given model in a filter in eval model