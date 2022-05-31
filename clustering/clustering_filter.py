from sklearn.cluster import DBSCAN

import matplotlib.pyplot as plt
import cv2
import numpy as np


def eliminate_noise(labels_array, frame_2d):
    """
    Takes the DBSCAN Labeled set and the 2d frame, then returns
    the corrected frame and labels array
    """
    frame_2d = np.delete(frame_2d, np.where(labels_array == -1), axis=0)
    labels_array = np.delete(labels_array, np.where(labels_array == -1), axis=0)

    return frame_2d, labels_array


frame = cv2.imread("/home/rvergnia/baboon-tracking/clustering/noisy.png")

# simplifies the image from 3d to 2d
twoD_frame = frame[:, :, 0]
x, y = np.where(twoD_frame == 255)
image = np.zeros((len(x), 2))
image[:, 0] = x
image[:, 1] = y

# creates clusters and eliminates noise from labels and 2dframe
db = DBSCAN(eps=4, min_samples=40).fit(image)
labels = db.labels_
image, c_labels = eliminate_noise(labels, image)
image = image.astype(np.uint32)
noiseless_frame = np.zeros_like(frame)
noiseless_frame[image[:, 0], image[:, 1]] = 255

# applies dilate filter and saves the residual frame
cv2.imwrite("noiseless.png", noiseless_frame)
noiseless = cv2.imread("/home/rvergnia/baboon-tracking/noiseless.png")
kernel = np.ones((5, 5), np.uint8)
dilated_noiseless = cv2.dilate(noiseless, kernel, iterations=1)
cv2.imwrite("dilate_noiseless.png", dilated_noiseless)


X = image[:, 0]
Y = image[:, 1]
plt.scatter(X, Y, 0.1, c=c_labels)
plt.show()

