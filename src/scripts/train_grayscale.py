from math import ceil, floor
import cv2
import torch
from torch import nn
import numpy as np
import skimage
from os.path import isfile
import adabound
import gc

thresh = 1e-10

class ColorSpaceTransformation(nn.Module):
    def __init__(self):
        nn.Module.__init__(self)

        self.input_layer = nn.Sequential(
            nn.Linear(3, 100),
            nn.ReLU(inplace=True)
        )
        self.hidden_layer = nn.Sequential(
            nn.Linear(100, 100),
            nn.ReLU(inplace=True)
        )
        self.output_layer = nn.Sequential(
            nn.Linear(100, 1),
        )

    def forward(self, x):
        x = self.input_layer(x)
        x = self.hidden_layer(x)
        x = self.output_layer(x)

        x = torch.clamp(x, 0, 1)

        return x

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# device = torch.device("cpu")
model = ColorSpaceTransformation().to(device)

optim = torch.optim.Adagrad(model.parameters(), lr=1e-6)
# optim = adabound.AdaBound(model.parameters(), lr=1, final_lr=1e-10)
# loss_func = nn.MSELoss()
loss_func = nn.L1Loss()

if isfile('./output/color_space_weights.pth'):
    model.load_state_dict(torch.load('./output/color_space_weights.pth'))

i = 0
while True:
    frame = np.random.randn(90, 160, 3).astype(np.float32)
    # frame[0, :, :] = [0, 0, 0]
    # frame[1, :, :] = [1, 1, 1]

    height, width, _ = frame.shape

    # Display the resulting frame
    frame_tensor = torch.Tensor(frame.transpose(2,0,1).reshape(3,-1).T).to(device)
    cv2.imshow('Frame', frame)
    
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_tensor = torch.Tensor(gray_frame.T.reshape(height * width).T).to(device)
    cv2.imshow('Gray Frame', gray_frame)

    nn_tensor = model.forward(frame_tensor)
    nn_frame = nn_tensor * 255
    nn_frame = nn_frame.cpu().detach().numpy().T.reshape(height, width).astype(
        np.uint8
    )

    cv2.imshow('NN Frame', nn_frame)

    # n = np.random.randint(len(gray_tensor) + 1)
    # loss = loss_func(gray_tensor[n], nn_tensor[n, 0])
    loss = loss_func(gray_tensor.unsqueeze(1), nn_tensor)

    if loss <= thresh:
        break

    optim.zero_grad()
    loss.backward()
    optim.step()

    if i % 10 == 0:
        print(F"min: {torch.min(nn_tensor)}, max: {torch.max(nn_tensor)}, loss: {loss}")
        torch.save(model.state_dict(), './output/color_space_weights.pth')

    i += 1

    # Press Q on keyboard to  exit
    if (cv2.waitKey(25) & 0xFF) == ord('q'):
        pass
        # break

print("done")

torch.save(model.state_dict(), './output/color_space_weights.pth')

# cv2.waitKey()

# Closes all the frames
cv2.destroyAllWindows()
