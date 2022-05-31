from turtle import window_width
import cv2
from cv2 import waitKey
import numpy as np
from numpy.random import randint
from random import random


background = np.zeros((415, 415, 3))

ellipsis = cv2.ellipse(
    background, (100, 100), (50, 20), 45, 0, 360, color=(255, 255, 255), thickness=-1,
)

print(ellipsis)

# transform image into array
# itterate through it and change the 255 values to 0 or 1 based on a probability coef

# print(ellipse_array)
# for row in ellipse_array:
#     for col in row:
#         if ellipsis[row, col] == 255 and random() < 0.7:
#             ellipsis[row, col] = 0

cv2.imshow("image", ellipsis)
waitKey(0)
