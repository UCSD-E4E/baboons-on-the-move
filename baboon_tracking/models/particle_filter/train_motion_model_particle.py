from baseline_model import *
from pathlib import Path 
import numpy as np
import pandas as pd
import os
import math
import pickle
import matplotlib.pyplot as plt

root = Path('../../..')

config = {}
config['k_nearest_baboons'] = 4 #getting the four nearest baboons per frame to consider(MUST BE EVEN)
config['k_historic_velocities'] = 4 #getting the four past velocities to consider
config['checkpoint_training'] = False
config['saved_path'] = 'saved_weights.pth' #path to save current model information (epoch, weights, etc...)
config['learning_rate'] = 0.0001 #lr
config['batch_size'] = 32 # Number of training samples per batch to be passed to network
config['val_split'] = 0.2 #ratio of val and training data
config['shuffle_dataset'] = True #shuffle data before start (TODO: change this if we use kfold?)
config['epochs'] = 100  # Number of epochs to train the model
config['early_stop'] = True  # Implement early stopping or not
config['early_stop_epoch'] = 3 # Number of epochs for which validation loss increases to be counted as overfitting
config['input_training_data'] = root / 'ml_data' / 'DJI_0870_velocity.csv'
config['kmeans_model_path'] = root / 'ml_data' / 'velocity_model.pkl'


#DO NOT CHANGE THE FOLLOWING 
config['input_dimension'] = config['k_nearest_baboons'] + config['k_historic_velocities'] + 1 #DON'T TOUCH THIS
config['validation_loss_path'] = '' #leave empty 
config['training_loss_path'] = '' #leave empty 
config['output_dimension'] = -1 #leave empty

#config checks
assert( config['k_nearest_baboons'] % 2 == 0 )
assert( os.path.isfile(config['input_training_data']) == True)
assert( os.path.isfile(config['kmeans_model_path']) == True)


#This is assuming the obvious assumption that a baboon only has one position per frame
#TODO : Assuming data is ordered by frame (increasing timesteps/frames)
training_data = pd.read_csv(config['input_training_data'])

frames_to_velocities = {} #Maps a single frame to a list of all the baboons, their id, position, and velocity

for idx, row in training_data.iterrows():
    current_frame = row.loc['frame']
    current_position = (row.loc['centroid_x'], row.loc['centroid_y'])
    current_velocity = row.loc['velocity']
    current_id = row.loc['baboon id']
    
    if current_frame not in frames_to_velocities:
        frames_to_velocities[current_frame] = []
    
    frames_to_velocities[current_frame].append((current_position, current_velocity, current_id))

"""
Returns the K physically nearest baboons to baboon_id at the given frame

Pre-pends with negative ones if there are less than k nearest baboons in the frame
"""
def get_k_nearest_baboons_velocities(frame, baboon_id):
    baboons_in_frame = frames_to_velocities[frame].copy()
    output = []
    
    target_position = (-1, -1)
    
    #get rid of the baboon we are considering
    for idx, baboon in enumerate(baboons_in_frame):
        if baboon[2] == baboon_id:
            target_velocity = baboons_in_frame[idx][0]
            del baboons_in_frame[idx]
            break
      
    if len(baboons_in_frame) <= config['k_nearest_baboons']:
        padded_output = list(np.ones(config['k_nearest_baboons'] - len(baboons_in_frame)) * -1)
        return padded_output.extend([item[1] for item in baboons_in_frame])
    
    for k_nearest_neighbor in range(config['k_nearest_baboons']):
        min_distance = math.inf
        min_velocity = -1
        min_idx = -1
        
        for idx, baboon in enumerate(baboons_in_frame):
            current_distance = np.linalg.norm(np.array(baboon[0]) - np.array(target_velocity))
            if current_distance < min_distance:
                min_distance = current_distance
                min_velocity = baboon[1]
                min_idx = idx
        
        output.append(min_velocity)
        del baboons_in_frame[min_idx]
        
    return output
            

#TODO : Must check for 'extended' periods of discountinuous frames for future potentially sparese labeled data
#TODO : Assuming data is ordered by frame (increasing timesteps/frames)
#TODO : Warning : if there are not enough K historic frames then we pre pad with negative ones

baboons_to_velocities = {} #maps the baboon's id to it's velocties and respective frames in a tuple

for idx, row in training_data.iterrows():
    current_frame = row.loc['frame']
    current_position = (row.loc['centroid_x'], row.loc['centroid_y'])
    current_velocity = row.loc['velocity']
    current_id = row.loc['baboon id']
    
    if current_id not in baboons_to_velocities:
        baboons_to_velocities[current_id] = []
        
    baboons_to_velocities[current_id].append((current_velocity, current_frame))

"""
Given a frame returns the k past velocities of the given baboon_id

Pre pads with negative ones if there are less than k previous frames available in the labeled data
"""
def get_k_past_velocities(current_frame, baboon_id):
    velocities = baboons_to_velocities[baboon_id]
    
    #annoying but I don't know how to do this easier
    frame_index = -1
    for idx, frame in enumerate(velocities):
        if frame[1] == current_frame:
            frame_index = idx
            break
            
    if frame_index == -1:
        raise RuntimeError('Frame does not exist in dataset for this baboon_id')
        
    if frame_index < config['k_historic_velocities']:
        padded_output = list(np.ones(config['k_historic_velocities'] - frame_index) * -1)   
        padded_output.extend([item[0] for item in velocities[:frame_index]])
        return padded_output
    
    else:
        return [item[0] for item in velocities[frame_index-config['k_historic_velocities'] : frame_index]]


#TODO : way too hard coded here. Make better

training_data = pd.read_csv(config['input_training_data'])

kmeans = pickle.load(open(config['kmeans_model_path'], 'rb'))
kmeans_centers_sorted = np.sort(np.array(kmeans.cluster_centers_).squeeze())
config['output_dimension'] = kmeans_centers_sorted.size + 1


print('labeling data')
# test_predict = np.array([10])
# print(kmeans.predict(test_predict.reshape(-1,1)))
#TODO : add the sitting still !!!
label_table = {}
label_table[0] = [1,0,0,0,0,0] #sitting
label_table[kmeans_centers_sorted[0]] = [0,1,0,0,0,0]
label_table[kmeans_centers_sorted[1]] = [0,0,1,0,0,0]
label_table[kmeans_centers_sorted[2]] = [0,0,0,1,0,0]
label_table[kmeans_centers_sorted[3]] = [0,0,0,0,1,0]
label_table[kmeans_centers_sorted[4]] = [0,0,0,0,0,1]




# [ target v, k nearest baboon's v, k' past velocities ]
# X = np.zeros((training_data.shape[0], config['input_dimension']))
# labels = np.zeros(())
X = []
labels = []

start_historic = 1 + config['k_nearest_baboons']


for idx, row in training_data.iterrows():
    current_frame = row.loc['frame']
    current_position = (row.loc['centroid_x'], row.loc['centroid_y'])
    current_velocity = row.loc['velocity']
    current_id = row.loc['baboon id']
    
    current_label = training_data.loc[(training_data['frame'] == (current_frame + 1)) & (training_data['baboon id'] == current_id)]
    if(current_label.empty):
        #last frame for baboon, therefore no label
        continue
        
    #create the label
    current_one_hot = []
    current_label_velocity = current_label['velocity'].to_numpy()
    if current_label_velocity[0] == 0:
        current_one_hot = label_table[0]
    else:
        kmeans_label = kmeans.predict(current_label_velocity.reshape(-1,1))[0]
        current_one_hot = label_table[ kmeans.cluster_centers_[kmeans_label][0] ]
    current_one_hot = np.array(current_one_hot)
    
    #create the datapoint
    current_datapoint = np.zeros(config['input_dimension'])
    current_datapoint[0] = current_velocity
    current_datapoint[1:start_historic] = get_k_nearest_baboons_velocities(current_frame, current_id)
    current_datapoint[start_historic:] = get_k_past_velocities(current_frame, current_id)
    
    X.append(current_datapoint)
    labels.append(current_one_hot)



X = np.array(X)
labels = np.array(labels)


#TODO : add weighted classes to save from an unbalanced dataset
# Check if your system supports CUDA
use_cuda = torch.cuda.is_available()

# Setup GPU optimization if CUDA is supported
if use_cuda:
    computing_device = torch.device("cuda")
    extras = {"num_workers": 1, "pin_memory": True}
    print("CUDA is supported")
else: # Otherwise, train on the CPU
    computing_device = torch.device("cpu")
    extras = False
    print("CUDA NOT supported")
    
 
if not config['checkpoint_training']:
    net = Nnet(config['input_dimension'], config['output_dimension']).to(computing_device)

optimizer = optim.Adam(net.parameters(),lr = config['learning_rate'])
criterion = nn.CrossEntropyLoss()


dataset = loader(X, labels)

batch_size = config['batch_size']
validation_split = config['val_split']
shuffle_dataset = config['shuffle_dataset']
random_seed= 69 

# Creating data indices for training and validation splits:
dataset_size = len(dataset)
indices = list(range(dataset_size))
split = int(np.floor(validation_split * dataset_size))
if shuffle_dataset :
    np.random.seed(random_seed)
    np.random.shuffle(indices)
train_indices, val_indices = indices[split:], indices[:split]

# Creating PT data samplers and loaders:
train_sampler = SubsetRandomSampler(train_indices)
valid_sampler = SubsetRandomSampler(val_indices)


train_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, 
                                               sampler=train_sampler)
    
validation_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size,
                                                sampler=valid_sampler)




# Track the loss across training
total_loss = []
avg_minibatch_loss = []
num_times_incraesed = 0
training_losses = []
validation_losses = []
N = 50




#TODO: Add dropout! When we do we MUST use model.eval() for val or testing and model.train() for training
prev_val_loss = float("inf")

for epoch in range(config['epochs']):    
    old_net_weights = net.state_dict().copy()
    old_optimizer = optimizer.state_dict().copy()
    
    print(f"Started training epoch : {epoch}" )
    

    N_minibatch_loss = 0.0
    total_epoch_loss = 0.0
    average_epoch_loss = 0.0
    num_minibatches = 0
    
     
    net.train() #turns dropout on

    # Get the next minibatch of images, labels for training
    for minibatch_count, (datapoints, labels) in enumerate(train_loader, 0):

        num_minibatches += 1
        # Zero out the stored gradient (buffer) from the previous iteration
        optimizer.zero_grad()
        # Put the minibatch data in CUDA Tensors and run on the GPU if supported
        datapoints, labels = datapoints.to(computing_device), labels.to(computing_device)
        # Perform the forward pass through the network and compute the loss
        outputs = net(datapoints.float())
        labels = torch.max(labels, 1)[1]
        
        #computing the CEL using the net and the labels
        loss = criterion(outputs, labels)
#         print(f'Minibatch {minibatch_count} loss : {loss.item()}')
        
        # Automagically compute the gradients and backpropagate the loss through the network
        loss.backward()
        total_epoch_loss += loss.item()

        # Update the weights
        optimizer.step()    
        # Add this iteration's loss to the total_loss
        total_loss.append(loss.item())
        N_minibatch_loss += loss
        
               
        
        if minibatch_count % N == 49:
            #Print the loss averaged over the last N mini-batches
            N_minibatch_loss /= N
            print(f'Epoch {epoch + 1}, average minibatch {minibatch_count+1} loss: {N_minibatch_loss}')
            # Add the averaged loss over N minibatches and reset the counter
            avg_minibatch_loss.append(N_minibatch_loss)
            N_minibatch_loss = 0.0
    
    average_epoch_loss = total_epoch_loss / num_minibatches
    print(f"Finished {epoch+ 1} epochs of training with average {average_epoch_loss} loss." )
    
    N_minibatch_val_loss = 0
    val_data_size = 0
    
    
    with torch.no_grad():
        net.eval() #turns dropout off
        print("validation starting: ")

        for minibatch_count, (datapoints, labels) in enumerate(validation_loader, 0):
            val_data_size += 1
            datapoints, labels = datapoints.to(computing_device), labels.to(computing_device)
            outputs = net(datapoints.float())
            val_loss = criterion(outputs, labels).item()
            N_minibatch_val_loss += val_loss

        N_minibatch_val_loss /= val_data_size
        print(f'Epoch {epoch + 1} average validation loss over {val_data_size} datapoints : {N_minibatch_val_loss}' )
        
        #early stopping
        if config['early_stop']:
            print(str(N_minibatch_val_loss) + ' vs' + str(prev_val_loss))

            if num_times_incraesed >= config['early_stop_epoch']:
                print('early stopping triggered')
                break
            if N_minibatch_val_loss > prev_val_loss:
                print('keeping old weights')
                num_times_incraesed += 1
                net.load_state_dict(old_net_weights)
                optimizer.load_state_dict(old_optimizer)
            else : 
                print('val is less than previous')
                num_times_incraesed = 0
                prev_val_loss = N_minibatch_val_loss

             
    training_losses.append(average_epoch_loss)
    validation_losses.append(N_minibatch_val_loss)


min_entries = min(len(training_losses), len(validation_losses))
epochs_plots = []
for i in range(min_entries):
    epochs_plots.append(i+1)
    
val_plots = training_losses[:min_entries]
train_plots = validation_losses[:min_entries]

plt.figure()
plt.plot(epochs_plots, val_plots, label='val loss')
plt.plot(epochs_plots, train_plots, label='train loss')
plt.legend(loc='upper right')
plt.xlabel('epochs')
plt.ylabel('cross entropy error')


