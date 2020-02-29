import cv2
import numpy as np
import time
import sys
import yaml

import baboon_tracking as bt
import baboon_tracking.registration
import baboon_tracking.foreground_extraction
from baboon_tracking.models.config import Config

def main():

    # load the data from the configuration file
    config = Config( 'config.yml' )

    # open the input video
    cap = cv2.VideoCapture( config.input_location )   
    if not cap.isOpened():
        print( "Error opening video stream or file: ", config.input_location )
        exit()
    
    # load important metadata from the video
    config.load_metadata( cap )

    # prepare to write to the output video
    out = cv2.VideoWriter( config.output_location, cv2.VideoWriter_fourcc(*'mp4v'), config.fps, (config.frame_width, config.frame_height))

    # set up tracker
    registration = bt.registration.ORB_RANSAC_Registration( config.history_frames, config.max_features, config.match_percent )
    fg_extraction = bt.foreground_extraction.VariableBackgroundSub_ForegroundExtraction( config.history_frames )

    tracker = bt.BaboonTracker(registration=registration, foreground_extraction=fg_extraction)
    #server = bt.ImageStreamServer(host='localhost', port='5672')

    start = time.perf_counter()
    curr_frame = 1

    while True:
        
        # Capture frame-by-frame
        success, frame = cap.read()

        if not success:
            break

        #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #gray = hsv[:,:,2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray = cv2.blur(gray, (2, 2))
        #gray = cv2.medianBlur(gray, 15)
        gray = cv2.GaussianBlur(gray,(5,5),0)

        frame_obj = bt.Frame(gray, curr_frame)

        print('image gathered')

        # cv2.imshow('Gray', cv2.resize(gray, (config['display']['width'], config['display']['height'])))

        # We need at least n frames to continue
        if (not tracker.is_history_frames_full()):
            tracker.push_history_frame(frame_obj)

            curr_frame = curr_frame + 1
            continue

        print('registering frames')

        # returns list of tuples of (shifted frames, transformation matrix)
        shifted_history_frames = tracker.shift_history_frames(frame_obj)

        print('frames registered')

        # splits tuple list into two lists
        Ms = [f[1] for f in shifted_history_frames]
        shifted_history_frames = [f[0] for f in shifted_history_frames]

        print('starting moving foreground')

        # generates moving foreground mask
        moving_foreground = tracker.generate_motion_mask(frame_obj, shifted_history_frames, Ms)

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        eroded = cv2.erode(moving_foreground, element)

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30))
        opened_mask = cv2.dilate(eroded, element)

        combined_mask = np.zeros(opened_mask.shape).astype(np.uint8)
        combined_mask[opened_mask == moving_foreground] = 255
        combined_mask[moving_foreground == 0] = 0

        # (height, width) = moving_foreground.shape

        # for y in range(1, height - 1):
        #     for x in range(1, width - 1):
        #         if moving_foreground[y, x] == 0:
        #             continue

        #         if moving_foreground[y - 1, x] != 0 or \
        #             moving_foreground[y, x - 1] != 0 or \
        #             moving_foreground[y + 1, x] != 0 or \
        #             moving_foreground[y, x + 1] != 0:
        #             continue

        #         moving_foreground[y, x] = 0

        print('moving foreground generated')

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12))
        dialated = cv2.dilate(combined_mask, element)
        eroded = cv2.erode(dialated, element)


        blend = cv2.addWeighted(frame, 0.75, cv2.cvtColor(eroded, cv2.COLOR_GRAY2BGR), 0.5, 0.0)          

        # Display the resulting frame
        #cv2.imshow('combined_mask', cv2.resize(combined_mask, (config['display']['width'], config['display']['height'])))
        cv2.imshow('blend', cv2.resize(blend, ( config.display_width , config.display_height )))
        #server.imshow(moving_foreground)
        #out.write(cv2.cvtColor(eroded, cv2.COLOR_GRAY2BGR))
        out.write(blend)

        tracker.push_history_frame(frame_obj)

        curr_time = time.perf_counter() - start
        percentage = curr_frame / config.frame_count
        estimate_total_time = curr_time / percentage
        time_per_frame = curr_time / curr_frame
        estimate_time_remaining = estimate_total_time - curr_time
        coefficient_of_performance = estimate_total_time / config.video_length

        print('curr_time: {}h, {}m, {}s'.format(round(curr_time / 60 / 60, 2), round(curr_time / 60, 2), round(curr_time, 2)))
        print('estimate_total_time: {}h, {}m, {}s'.format(round(estimate_total_time / 60 / 60, 2), round(estimate_total_time / 60, 2), round(estimate_total_time, 2)))
        print('estimate_time_remaining: {}h, {}m, {}s'.format(round(estimate_time_remaining / 60 / 60, 2), round(estimate_time_remaining / 60, 2), round(estimate_time_remaining, 2)))
        print('time_per_frame: {}s'.format(round(time_per_frame, 2)))
        print('video_time_complete: {}s'.format(round(curr_frame / config.fps)))
        print('percentage: {}%'.format(round(percentage * 100, 2)))
        print('coefficient_of_performance: {}%'.format(round(coefficient_of_performance * 100, 2)))
        print('')

        curr_frame = curr_frame + 1

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q') or curr_time > 5 * 60 * 60 or curr_frame == config.max_frames:
            break


    # When everything done, release the video capture object
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
