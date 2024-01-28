import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing
import sys

import baboon_tracking as bt
from library.config import *

configs["blob_det_params"] = BLOB_DET_PARAMS


def main():
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(INPUT_MASK)

    cap_orig = cv2.VideoCapture(INPUT_VIDEO)

    # Check if camera opened successfully
    if cap.isOpened() == False:
        print("Error opening video stream or file")
        sys.exit()

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter(
        OUTPUT_MASK_BLOB_DETECTION,
        cv2.VideoWriter_fourcc(*"mp4v"),
        20.0,
        (DISPLAY_WIDTH, DISPLAY_HEIGHT),
    )

    # Process original video if provided
    if cap_orig.isOpened() and int(
        cap_orig.get(3) == frame_width and cap_orig.get(4) == frame_height
    ):
        using_orig = True

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

    # create tracker
    blob_detector = bt.blob_detection.OpenCV_Simple_BlobDetection(configs)
    tracker = bt.BaboonTracker(configs, blob_detection=blob_detector, pool=pool)

    start = time.clock()
    # Read until video is completed
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        orig_ret, orig_frame = cap_orig.read()
        if ret == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            moving_foreground = gray

            blob_keypoints = tracker.detect_blobs(moving_foreground)

            # draw detected blobs
            frame_with_blobs = cv2.drawKeypoints(
                orig_frame,
                blob_keypoints,
                np.array([]),
                (0, 0, 255),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )
            mask_with_blobs = cv2.drawKeypoints(
                frame,
                blob_keypoints,
                np.array([]),
                (0, 0, 255),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )

            # Display the resulting frame

            # cv2.imshow('moving_foreground', cv2.resize(moving_foreground, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))
            cv2.imshow(
                "detected_blobs",
                cv2.resize(frame_with_blobs, (DISPLAY_WIDTH, DISPLAY_HEIGHT)),
            )
            # display the frame that keypoints are being found from as well as keypoints detected
            cv2.imshow(
                "detected_blobs_mask",
                cv2.resize(mask_with_blobs, (DISPLAY_WIDTH, DISPLAY_HEIGHT)),
            )

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord("q"):
                break

        # Break the loop
        else:
            break

    # When everything done, release the video capture object
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
