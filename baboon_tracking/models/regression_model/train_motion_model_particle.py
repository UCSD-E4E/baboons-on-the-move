from baseline_model import *
from pathlib import Path 
import numpy as np
import pandas as pd
import os
import math
import code
import pickle
import matplotlib.pyplot as plt
from tensorboardX import SummaryWriter
from datetime import date


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
config['epochs'] = 1  # Number of epochs to train the model
config['early_stop'] = True  # Implement early stopping or not
config['early_stop_epoch'] = 3 # Number of epochs for which validation loss increases to be counted as overfitting
# config['kmeans_model_path'] = root / 'ml_data' / 'velocity_model.pkl'
config['data_output_path'] = './data.npy'
config['labels_output_path'] = './labels.npy'



#DO NOT CHANGE THE FOLLOWING 
config['input_dimension'] = config['k_nearest_baboons'] + config['k_historic_velocities'] + 1 #DON'T TOUCH THIS
config['validation_loss_path'] = '' #leave empty 
config['training_loss_path'] = '' #leave empty 
config['output_dimension'] = -1 #leave empty

#config checks
assert( config['k_nearest_baboons'] % 2 == 0 )
# assert( os.path.isfile(config['kmeans_model_path']) == True)

today = date.today()
d1 = today.strftime("%d_%m_%Y")
writer = SummaryWriter(f'motion_model_tensorboard_{d1}', flush_secs=1)



# kmeans = pickle.load(open(config['kmeans_model_path'], 'rb'))
# kmeans_centers_sorted = np.sort(np.array(kmeans.cluster_centers_).squeeze())
config['output_dimension'] = 1 # 1 for regression


X = np.load(config['data_output_path'])
labels = np.load(config['labels_output_path'])

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
criterion = nn.MSELoss()


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
        outputs = outputs.reshape(-1)
        #labels = torch.max(labels, 1)[1]
        labels = labels.reshape(-1).float()
       
        '''
        print("outputs", outputs)
        print(outputs.shape)
        print("labels:", labels)
        print(labels.shape)
        '''
        
        #computing the CEL using the net and the labels
        loss = criterion(outputs, labels)
        print("loss: ", loss)
#         print(f'Minibatch {minibatch_count} loss : {loss.item()}')
        
        # Automagically compute the gradients and backpropagate the loss through the network
        loss.backward()
        total_epoch_loss += loss.item()

        writer.add_scalar('loss_train/loss', loss.item(), minibatch_count)
        writer.flush()

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
            labels = torch.max(labels, 1)[1]

            val_loss = criterion(outputs, labels).item()
            N_minibatch_val_loss += val_loss

        N_minibatch_val_loss /= val_data_size
        print(f'Epoch {epoch + 1} average validation loss over {val_data_size} datapoints : {N_minibatch_val_loss}' )
        writer.add_scalar('loss_train/val', N_minibatch_val_loss, epoch)
        writer.flush()

        
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


torch.save(net.state_dict(), './net.pth'  )

