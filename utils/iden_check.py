import cv2
import numpy as np
import hashlib
import sys

def main():

    if len( sys.argv ) < 3:
        print("Please pass paths to the videos you'd like to compare.")
        return 1

    DIFF_VIDEO_1 = sys.argv[ 1 ]
    DIFF_VIDEO_2 = sys.argv[ 2 ]

    cap1 = cv2.VideoCapture( DIFF_VIDEO_1 )
    cap2 = cv2.VideoCapture( DIFF_VIDEO_2 )

    print( f"Comparing {DIFF_VIDEO_1} and {DIFF_VIDEO_2}: " )

    # check if camera opened successfully
    if(cap1.isOpened() == False):
        print("Error opening video 1")
        exit()
    if(cap2.isOpened() == False):
        print("Error opening video 2")
        exit()

    # check if videos have same dimensions
    if(cap1.get(3) != cap2.get(3) or cap1.get(4) != cap2.get(4)):
        print("Video 1 has dimensions (", cap1.get(3), ", ", cap1.get(4), "), but video 2 has dimensions (", cap2.get(3), ",", cap2.get(4), ")")
        exit()

    frame_count = min( cap1.get(cv2.CAP_PROP_FRAME_COUNT), cap2.get(cv2.CAP_PROP_FRAME_COUNT) )
    frame_number = 0
    frame_width = int(cap1.get(3))
    frame_height = int(cap1.get(4))

    while(cap1.isOpened() and cap2.isOpened()):

        # show a progress bar for long-running frame-wise comparisons
        if frame_count > 20:  
            i = int( frame_number / (frame_count / 20) )
            sys.stdout.write("Progress: [{0}] {1:.0f}%      \r".format( '#' * (i+1) + ' ' * (19 - i), frame_number * 100 / frame_count ))
            sys.stdout.flush()

        frame_number += 1

        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break

        if np.any( frame1 != frame2 ):
            print(f"FAIL: The videos are NOT framewise identical.")
            return

    cap1.release()
    cap2.release()
    
    print(f"SUCCESS. The videos are framewise identical up to frame {frame_number}.")

if __name__ == '__main__':
    main()
