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

def main():
    #local variables of aggregiated run times
    intersect_time = 0
    union_time = 0
    dissimilarity_time = 0
    weights_time = 0
    zero_time = 0

    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture('DJI_0769.MP4')
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video stream or file")

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('outpy.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width,frame_height))

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

    start = time.clock()
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            cv2.imshow('Gray', cv2.resize(gray, (1600, 900)))

            # We need at least n frames to continue
            if (len(history_frames) < history_frame_count):
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

            #including second start time for individual functions
            start2 = time.clock()
            intersects = [intersect_frames(z[0], z[1]) for z in zip(grouped_shifted_history_frames, grouped_quantized_frames)]
            curr_time2 = time.clock() - start2
            intersect_time += curr_time2

            start2 = time.clock()
            union = union_frames(intersects)
            curr_time2 = time.clock() - start2
            union_time += curr_time2

            start2 = time.clock()
            history_of_dissimilarity = get_history_of_dissimilarity(shifted_history_frames, quantized_frames)
            curr_time2 = time.clock() - start2
            dissimilarity_time += curr_time2

            start2 = time.clock()
            weights = get_weights(quantized_frames)
            curr_time2 = time.clock() - start2
            weights_time += curr_time2

            start2 = time.clock()
            frame_new = zero_weights(gray, weights)
            union_new = zero_weights(union, weights)
            curr_time2 = time.clock() - start2
            zero_time += curr_time2

            foreground = np.absolute(frame_new.astype(np.int32) - union_new.astype(np.int32)).astype(np.uint8)

            moving_foreground = get_moving_foreground(weights, foreground, history_of_dissimilarity)

            # This cleans up the edges after performing image registration.
            for mask in masks:
                moving_foreground = np.multiply(moving_foreground, mask)

            # Display the resulting frame
            cv2.imshow('moving_foreground', cv2.resize(moving_foreground, (1600, 900)))
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
    return intersect_time, union_time, dissimilarity_time, weights_time, zero_time

if __name__ == '__main__':
    #returning runtimes
    intersect_time, union_time, dissimilarity_time, weights_time, zero_time = main()
    #Creating txt file
    f = open( 'times_of_functions.txt', 'w' )
    f.write( 'intersect: ' + str(intersect_time))
    f.write('\n')
    f.write('union: ' + str(union_time))
    f.write('\n')
    f.write('dissimilarity: ' + str(dissimilarity_time))
    f.write('\n')
    f.write('weights: ' + str(weights_time))
    f.write('\n')
    f.write('zero: ' + str(zero_time))
    f.close()
