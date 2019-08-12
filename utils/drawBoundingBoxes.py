#this script runs with the inputs already being of the format (xlt, ylt) (xbr,ybr)

#import packages
import cv2
import numpy as np
import re

#refer to txt files
groundtruthfolder = "../groundtruth_drawing/"
hypothesesfolder = "../hypotheses_drawing/"

#frame number, which frame to compare
frame_num = 81

#files that you want to check
groundtruth_file = groundtruthfolder+"frame"+str(frame_num)+".txt"
hypothesis_file = hypothesesfolder+"frame"+str(frame_num)+".txt"
#draw image
img = np.zeros((3840,2160,3), np.uint8)

#Extract Ground Truth values and draw rectangles
with open(groundtruth_file) as txt_file: #+ will create a file with the right name, if it doesn't exist
    for line in txt_file:
         [xtl, ytl, xbr, ybr] = re.findall("\d+\.\d+", line)
         cv2.rectangle(img, (int(float(xtl)), int(float(ytl))), (int(float(xbr)), int(float(ybr))),(0,255,0),3)

#Extract Hypotheses values and draw rectangles
with open(hypothesis_file) as txt_file: #+ will create a file with the right name, if it doesn't exist
    for line in txt_file:
         [xtl, ytl, xbr, ybr] = re.findall("\d+\.\d+", line)
         print((int(float(xtl)), int(float(ytl))), (int(float(xbr)), int(float(ybr))))
         cv2.rectangle(img, (int(float(xtl)), int(float(ytl))), (int(float(xbr)), int(float(ybr))),(255,0,0),3)

#show image

cv2.imshow('dark', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
