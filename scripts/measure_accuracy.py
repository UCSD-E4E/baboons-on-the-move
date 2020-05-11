import cv2
import pandas as pd
#from pandas import Series, DataFrame
import argparse

parser = argparse.ArgumentParser(description="Calculates accuracy of centroid models.")
parser.add_argument('label_input', help='CSV file containing true centroid values. This can be made from converting research XML files from LABEL_PARTY folder using research_centroids.py')
parser.add_argument('test_input', help='CSV file to test, formatted with labels /"#, frame, x, y/"')
args = parser.parse_args()

label_df = pd.read_csv(args.label_input)
test_df = pd.read_csv(args.test_input)

label_df = label_df.sort_values('frame')
test_df = test_df.sort_values('frame')

label_df.to_csv('./testlabel.txt')
test_df.to_csv('./testdata.txt')