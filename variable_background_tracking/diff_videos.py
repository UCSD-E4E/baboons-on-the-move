import cv2
import numpy as np

from config import *

def main():

    cap1 = cv2.VideoCapture("../data/outpy_blur4x4.mp4")
    cap2 = cv2.VideoCapture("../data/outpy_nonblur.mp4")

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

    frame_width = int(cap1.get(3))
    frame_height = int(cap1.get(4))

    out = cv2.VideoWriter("./diff_output.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (frame_width, frame_height))

    while(cap1.isOpened() and cap2.isOpened()):
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if ret1 == True and ret2 == True:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            cv2.imshow("Gray1", cv2.resize(gray1, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))
            cv2.imshow("Gray2", cv2.resize(gray2, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))

            # calculate frame diff
            union = cv2.bitwise_or(gray1, gray2)
            intersect = cv2.bitwise_and(gray1, gray2)
            diff = cv2.bitwise_and(union, cv2.bitwise_not(intersect))

            cv2.imshow("Diff", cv2.resize(diff, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))
            out.write(cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR))

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

    cap1.release()
    cap2.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
