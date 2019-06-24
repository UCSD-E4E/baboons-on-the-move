import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing

from collections import deque
from registration import register

history_frame_count = 10

history_frames = deque([])
def push_history_frame(frame):
    if len(history_frames) == history_frame_count:
        history_frames.popleft()

    history_frames.append(frame)

def shift_frame(input):
    frame = input[0]
    previous_frame = input[1]

    M = register(previous_frame, frame)

    return (cv2.warpPerspective(previous_frame, M, (previous_frame.shape[1], previous_frame.shape[0])).astype(np.uint8), M)

def quantize(frame):
    return (frame.astype(np.float32) * 10 / 255).astype(np.int8)

def intersect_frames(frames, q_frames):
    print('intersect')

    mask = (np.abs(q_frames[0] - q_frames[1]) <= 1).astype(np.float64)
    combined = (np.multiply(skimage.img_as_float(frames[0]), mask) + np.multiply(skimage.img_as_float(frames[1]), mask)) / 2.0

    return skimage.img_as_ubyte(combined)

def union_frames(frames):
    print('union')

    union = np.zeros(frames[0].shape).astype(np.uint8)

    for f in frames:
        union[union == 0] = f[union == 0]

    return union

def get_history_of_dissimilarity(frames, q_frames):
    print('dissimilarity')

    dissimilarity = np.zeros(frames[0].shape).astype(np.uint32)

    for i in range(len(frames)):
        if i == 0:
            continue

        mask = (np.abs(q_frames[i] - q_frames[i - 1]) > 1).astype(np.uint32)
        dissimilarity = dissimilarity + np.multiply(np.abs(frames[i].astype(np.int32) - frames[i - 1].astype(np.int32)), mask)

    return (dissimilarity / len(frames)).astype(np.uint8)

def get_weights(q_frames):
    print('weights')

    weights = np.zeros(q_frames[0].shape).astype(np.uint8)

    for i, q in enumerate(q_frames):
        if i == 0:
            continue

        mask = (np.abs(q_frames[i] - q_frames[i - 1]) <= 1).astype(np.uint8)
        weights = weights + mask

    return weights

def zero_weights(frame, weights):
    print('zero')

    f = frame.copy()
    f[weights >= history_frame_count - 1] = 0

    return f

def get_moving_foreground(weights, foreground, dissimilarity):
    history_frame_count_third = math.floor(float(history_frame_count - 1) / 3)
    third_gray = 255.0 / 3.0

    weights_low = (weights <= history_frame_count_third).astype(np.uint8)
    weights_medium = np.logical_and(history_frame_count_third < weights, weights < history_frame_count - 1).astype(np.uint8) * 2

    weight_levels = weights_low + weights_medium

    foreground_low = (foreground <= math.floor(third_gray)).astype(np.uint8)
    foreground_medium = ((math.floor(third_gray) < foreground) + (foreground < math.floor(2 * third_gray))).astype(np.uint8) * 2
    foreground_high = (foreground >= math.floor(2 * third_gray)).astype(np.uint8) * 3

    foreground_levels = foreground_low + foreground_medium + foreground_high

    dissimilarity_low = (dissimilarity <= math.floor(third_gray)).astype(np.uint8)
    dissimilarity_medium = ((math.floor(third_gray) < dissimilarity) + (dissimilarity < math.floor(2 * third_gray))).astype(np.uint8) * 2
    dissimilarity_high = (dissimilarity >= math.floor(2 * third_gray)).astype(np.uint8) * 3

    dissimilarity_levels = dissimilarity_low + dissimilarity_medium + dissimilarity_high

    moving_foreground = np.logical_and(weight_levels == 2, np.greater_equal(foreground_levels, dissimilarity_levels)).astype(np.uint8)
    moving_foreground = moving_foreground + np.logical_and(weight_levels == 1, np.logical_and(dissimilarity_levels == 1, np.greater(foreground_levels, dissimilarity_levels))).astype(np.uint8)

    return moving_foreground * 255

def main():  
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture('DJI_0769.MP4')
    
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('outpy.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (frame_width,frame_height))

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

if __name__ == '__main__':
    main()