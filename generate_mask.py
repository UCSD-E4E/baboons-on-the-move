import cv2
import numpy as np
import time
import multiprocessing
import sys
import yaml

import baboon_tracking as bt
import baboon_tracking.registration
import baboon_tracking.foreground_extraction

multiprocessing.set_start_method('spawn', True)

def main():
    with open('config.yml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()

    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(config['input'])

    print(config['input'])
    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video stream or file: ", config['input'])
        exit()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    out = cv2.VideoWriter(config['output'], cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width,frame_height))

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

    # set up tracker
    registration = bt.registration.ORB_RANSAC_Registration(config)
    fg_extraction = bt.foreground_extraction.VariableBackgroundSub_ForegroundExtraction(config)

    tracker = bt.BaboonTracker(config=config, registration=registration, foreground_extraction=fg_extraction, pool=pool)
    #server = bt.ImageStreamServer(host='localhost', port='5672')

    start = time.clock()
    curr_frame = 1
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            #cv2.imshow('Gray', cv2.resize(gray, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))

            # We need at least n frames to continue
            if (len(tracker.history_frames) < config['history_frames']):
                tracker.push_history_frame(gray)
                continue

            # returns list of tuples of (shifted frames, transformation matrix)
            shifted_history_frames = tracker.shift_history_frames(gray)

            # splits tuple list into two lists
            Ms = [f[1] for f in shifted_history_frames]
            shifted_history_frames = [f[0] for f in shifted_history_frames]

            # generates moving foreground mask
            moving_foreground = tracker.generate_motion_mask(gray, shifted_history_frames, Ms, curr_frame)

            # Display the resulting frame
            cv2.imshow('moving_foreground', cv2.resize(moving_foreground, (config['display']['width'], config['display']['height'])))
            #server.imshow(moving_foreground)
            out.write(cv2.cvtColor(moving_foreground, cv2.COLOR_GRAY2BGR))

            tracker.push_history_frame(gray)

            curr_time = time.clock() - start

            percentage = curr_frame / frame_count

            estimate_total_time = curr_time / percentage

            print('curr_time: ' + str(curr_time))
            print('estimate_total_time: ' + str(estimate_total_time))
            print('percentage: ' + str(percentage))

            curr_frame = curr_frame + 1

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
