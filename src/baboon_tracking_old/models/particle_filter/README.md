# General Notes 
ipynb have been converted to py files so that they can be more comfortably used in the nautilus environment for training

# Fully Trained Model : 
https://drive.google.com/file/d/1gPmGbGUJsBaN4G_LSLPstguJGMzG-ViI/view?usp=sharing

# How to Train 
1. A csv containing the velocities, centroid position, and direction of motion is always required (e.g : https://drive.google.com/file/d/1TnvxPk0-3TXeKXBKPRT3jVGX0ULoWaQW/view?usp=sharing)  
2. Run the kmean_clustering.py file (be careful to use the right input_velocitioes_csv path). It will output a .pkl kmeans model in the same directory that it found the csv in step 1.  
3. Run the preprocess_data.py that will get the data in a format for training. More specifically findiong the nearest baboons per frame and the historic velocities for a given baboon.  Outputted data is found in this directory at data.npy and labels.npy.  
4. Train the model using the train_motion_model_particle (CUDA enabled GPU is recommended). Model is outputted at net.pth in the current directory along with the tensorboard metrics in its own directory.  
5. Use given model in particle filter in eval model