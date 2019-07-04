import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing

from collections import deque
from registration import *

def main():
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture('../data/DJI_0769.MP4')

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video stream or file")

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('result.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (frame_width,frame_height))

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

    start = time.clock()


    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # We need at least n frames to continue
            if (len(history_frames) < history_frame_count):
                push_history_frame(frame, gray)
                continue

            # WARNING this returns color frames, not gray frames like variable_background_tracking
            shifted_history_frames = pool.map(shift_frame, [(gray, f) for f in zip(history_frames_gray, history_frames)])

            # Create a new bg subtractor each cycle, cuz we always shift all prev frames to location of current frame
            # THIS CAN BE A LOT MORE EFFICIENT IF WE FIND ONE LOCATION TO SHIFT ALL FRAMES TOO
            fgbg = cv2.createBackgroundSubtractorMOG2(history=history_frame_count)
            #fgbg = cv2.createBackgroundSubtractorKNN(history=history_frame_count)

            # apply bg subtraction to all history frames (can this be parallelized?)
            for shifted_frame, _ in shifted_history_frames:
                shifted_frame = cv2.blur(shifted_frame, (5,5))
                fgbg.apply(shifted_frame)
            blurred_frame = cv2.blur(frame, (5,5))
            fgmask = fgbg.apply(blurred_frame)

            # Display the resulting frame
            cv2.imshow('frame', cv2.resize(shifted_frame,(1600, 900)))
            cv2.imshow('fgmask', cv2.resize(fgmask, (1600, 900)))
            out.write(cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR))

            push_history_frame(frame, gray)

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
