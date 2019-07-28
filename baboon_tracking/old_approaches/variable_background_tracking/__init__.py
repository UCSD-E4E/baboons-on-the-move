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

def main():
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(INPUT_VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video stream or file")
        exit()

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter(OUTPUT_MASK, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width,frame_height))

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

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
                push_history_frame(gray)
                continue

            shifted_history_frames = pool.map(shift_frame, [(gray, f) for f in history_frames])

            Ms = [f[1] for f in shifted_history_frames]
            shifted_history_frames = [f[0] for f in shifted_history_frames]

            quantized_frames = pool.map(quantize, [f for f in shifted_history_frames])

            masks = [cv2.warpPerspective(np.ones(gray.shape), M, (gray.shape[1], gray.shape[0])).astype(np.uint8) for M in Ms]

            frame_group_index = range(len(shifted_history_frames))
            frame_group_index = [(r, r + 1) for r in frame_group_index[::2]]

            grouped_shifted_history_frames = [(shifted_history_frames[g[0]], shifted_history_frames[g[1]]) for g in frame_group_index]
            grouped_quantized_frames = [(quantized_frames[g[0]], quantized_frames[g[1]]) for g in frame_group_index]

            # choose to use new or old intersects function
            if(ACTIVE_INTERSECT == 1):
                intersect_frames = intersect_frames_old

            intersects = [intersect_frames(z[0], z[1]) for z in zip(grouped_shifted_history_frames, grouped_quantized_frames)]
            union = union_frames(intersects)

            history_of_dissimilarity = get_history_of_dissimilarity(shifted_history_frames, quantized_frames)

            weights = get_weights(quantized_frames)

            frame_new = zero_weights(gray, weights)
            union_new = zero_weights(union, weights)

            foreground = np.absolute(frame_new.astype(np.int32) - union_new.astype(np.int32)).astype(np.uint8)

            moving_foreground = get_moving_foreground(weights, foreground, history_of_dissimilarity)

            # This cleans up the edges after performing image registration.
            for mask in masks:
                moving_foreground = np.multiply(moving_foreground, mask)

            # Display the resulting frame
            cv2.imshow('moving_foreground', cv2.resize(moving_foreground, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))
            out.write(cv2.cvtColor(moving_foreground, cv2.COLOR_GRAY2BGR))

            push_history_frame(gray)

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
