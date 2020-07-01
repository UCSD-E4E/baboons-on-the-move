import code
from xml.etree import ElementTree as ET
import math
import cv2
import csv
import numpy as np
import argparse
import ntpath
from pathlib import Path
import os


parser = argparse.ArgumentParser(description='Generate velocities given xml')
parser.add_argument('--input', '-i', required=True, type=str)
parser.add_argument('--output', '-o', default='./../output/velocties.csv', type=str)
args = parser.parse_args()


root_path = Path('./../')
if not os.path.isfile(args.input):
    assert RuntimeError('Given input xml file does not exist')
filename, extension = os.path.splitext(ntpath.basename(args.input))
if extension != '.xml':
    assert RuntimeError('Given input file is not an xml')
args.output = root_path / 'output' / f'{filename}.csv'

# Edit these as necessary.
VIDEO_FILEPATH = "./../data/input.mp4"

# Get fps of video
cap = cv2.VideoCapture(VIDEO_FILEPATH)
FPS = cap.get(cv2.CAP_PROP_FPS)

# Loads XML data into python using etree package


def loadXML(xmlPath):
    XMLtree = ET.parse(xmlPath)
    root = XMLtree.getroot()
    return root

# Finds centroid to be center point between top-left and bottom-right bounding points


def getCentroid(boxElement):
    xtl = float(boxElement.get('xtl'))
    ytl = float(boxElement.get('ytl'))
    xbr = float(boxElement.get('xbr'))
    ybr = float(boxElement.get('ybr'))
    centroid_x = xtl + ((xbr-xtl)/2)
    centroid_y = ytl + ((ybr-ytl)/2)
    return centroid_x, centroid_y

# Computes velocity between previous position (centroid1) and current position(cenroid2)


def computeVelocity(centroid1, centroid2, FPS=FPS):
    if centroid1 is None or centroid2 is None:
        return None
    #Velocity = Distance / Time
    # Distance Formula = sqrt((x2-x1)^2 + (y2-y1)^2 )
    distance = math.sqrt(math.pow(centroid2[0]-centroid1[0], 2) + math.pow(centroid2[1]-centroid1[1], 2))

    return distance/(1/FPS)


# Computes direction in radians
def computeDirection(centroid1, centroid2, FPS=FPS):
    if centroid1 is None or centroid2 is None:
        return None

    return math.atan2(centroid2[1]-centroid1[1], centroid2[0]-centroid1[0])  # in radians


# Outputs a CSV file containing headers "baboon id", "frame", "centroid_x", "centroid_y", "velocity"
def outputToFile(fileContents, OUTPUT_FILEPATH=args.output):
    with open(OUTPUT_FILEPATH, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(fileContents)


print("Loading XML into Python")
XML = loadXML(args.input)
print("Loaded file ", args.input)

csvContents = [['baboon id', 'frame', 'centroid_x', 'centroid_y', 'velocity', 'direction']]

# iter through each baboon in file - labeled "track" in XML
for baboon in XML.iter('track'):
    # prev centroid used to displace velocity
    last_centroid = None
    # iter through each frame the baboon appears in - labeled "box" in XML
    for box in baboon.iter('box'):
        # get centroid from bounding box - returns set with x-dim at 0 & y-dim at 1
        centroid = getCentroid(box)
        velocity = computeVelocity(last_centroid, centroid)
        direction = computeDirection(last_centroid, centroid)

        if last_centroid is not None:
            csvContents.append([baboon.get('id'), box.get('frame'), centroid[0], centroid[1], velocity, direction])

        last_centroid = centroid

print("Velocity computed, outputting to ", args.output)
outputToFile(csvContents)
print("Completed.")
