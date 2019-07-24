import cv2
import numpy as np
import math
import cmath

from registration import register

def shift_frame(frame, previous_frame):
    M = register(frame, previous_frame)

    previous_pixel = np.fft.ifft2(previous_frame).real.astype(np.uint8)

    return cv2.warpAffine(previous_pixel, M, (previous_pixel.shape[1], previous_pixel.shape[0])).astype(np.uint8)

def main():  
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture('DJI_0769.MP4')
    
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
    
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            size = 600

            frame = frame[size:(size + size), size:(size + size)]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fft_frame_1 = np.fft.fft2(gray)
            frame1 = frame

            ret, frame = cap.read()
            frame = frame[(size):(size + size), (size + 100):(size + size + 100)]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fft_frame_2 = np.fft.fft2(gray)

            shifted_frame = shift_frame(fft_frame_1, fft_frame_2)

            # Display the resulting frame
            cv2.imshow('Frame1', cv2.resize(frame1, (625, 625)))
            cv2.imshow('Frame2', cv2.resize(frame, (625, 625)))
            cv2.imshow('ShiftedFrame', cv2.resize(shifted_frame, (625, 625)))
            
            break
        # Break the loop
        else: 
            break

    while True:
        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    
    # When everything done, release the video capture object
    cap.release()
    
    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()