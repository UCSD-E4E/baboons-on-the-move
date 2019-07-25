import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing

from collections import deque
from registration import register

from foreground_extraction import *
from config import *

from BaboonDetector import BaboonDetector

def main():
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(INPUT_VIDEO)

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video stream or file")
        exit()

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter(OUTPUT_MASK, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (frame_width,frame_height))

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

    # Initialize baboon detector object
    configs = {
        'registration_strategy': 'orb'
    }

    tracker = BaboonTracker(configs)

    start = time.clock()
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            cv2.imshow('Gray', cv2.resize(gray, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))

            # We need at least n frames to continue
            if (len(history_frames) < HISTORY_FRAME_COUNT):
                tracker.push_history_frame(gray)
                continue

            # returns list of tuples of (shifted frames, transformation matrix)
            shifted_history_frames = tracker.shift_history_frames()

            # splits tuple list into two lists
            Ms = [f[1] for f in shifted_history_frames]
            shifted_history_frames = [f[0] for f in shifted_history_frames]

            # generates moving foreground mask
            moving_foreground = tracker.generate_motion_mask(shifted_history_frames, Ms)

            # Display the resulting frame
            cv2.imshow('moving_foreground', cv2.resize(moving_foreground, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))
            out.write(cv2.cvtColor(moving_foreground, cv2.COLOR_GRAY2BGR))

            tracker.push_history_frame(gray)

            curr_time = time.clock() - start

            print('curr_time: ' + str(curr_time))

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q') or curr_time > 5 * 60 * 60:
                break

        # Break the loop
        else:
            break

    # When everything done, release the video capture object
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
