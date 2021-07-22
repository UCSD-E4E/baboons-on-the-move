import numpy as np

# NumPy is a general-purpose array-processing package. It provides a high-performance multidimensional array object,
# and tools for working with these arrays. It is the fundamental package for scientific computing with Python.
import cv2

# OpenCV-Python is a library of Python bindings designed to solve computer vision problems. cv2. imread() method
# loads an image from the specified file. If the image cannot be read (because of missing file, improper permissions,
# unsupported or invalid format) then this method returns an empty matrix.
# Cv2.VideoCapture()-lass for video capturing from video files, image sequences or cameras.
##Open the webcam, typically device 0, if multiple webcams use 0,1,2,....
##set up output video compression method, output file, frame rate and image size
capture = cv2.VideoCapture(r"C:\Users\sydni\Downloads\input.mp4")
# width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
ret = capture.set(3, frame_width)
# height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
ret = capture.set(4, frame_height)
# Video writer class.
# The class provides C++ API for writing video files or image sequences.
# In order to encode the video in Python.a four character
# string is used to define the coding method
fourcc = cv2.VideoWriter_fourcc(*"XPID")
out = cv2.VideoWriter("output8.avi", fourcc, 20.0, (frame_width, frame_height))
# Returns true if video capturing has been initialized already.
# If the previous call to VideoCapture constructor or VideoCapture::open() succeeded, the method returns true
while capture.isOpened():
    # ret is a boolean variable that returns true if the frame is available.
    # frame is an image array vector captured based on the default frames per second defined explicitly or implicitly
    ret, frame = capture.read()
    if ret is True:
        # "Frame" will get the next frame in the camera (via "cap"). "Ret" will obtain return value from getting the
        # camera frame, either true of false. I recommend you to read the OpenCV tutorials(which are highly detailed)
        # like this one for face recognition:
        # frame = cv2.resize(frame, (640, 480))
        # OpenCV provides cv2.gaussianblur() function to
        # apply Gaussian Smoothing on the input source image. Following is the syntax of GaussianBlur() function :
        # cv2.GaussianBlur(src, ksize, sigmaX[, dst[, sigmaY[, borderType=BORDER_DEFAULT]]] )
        # output image----dst
        gaussianblur = cv2.GaussianBlur(frame, (5, 5), 0)
        dst = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
        # write the flipped frame
        out.write(frame)
        cv2.imshow("frame", dst)
        # cv2.imshow(window_name, image)
        # A string representing the name of the window in which image to be displayed.
    else:
        break
    # .waitKey(0) will display the window infinitely until any keypress (it is suitable for image display).
    # 2.waitKey(1) will display a frame for 1 ms, after which display will be automatically closed. Since the OS has a
    # minimum time between switching threads, the function will not wait exactly 1 ms, it will wait at least 1 ms,
    # depending on what else is running on your computer at that time. So, if you use waitKey(0) you see a still
    # image until you actually press something while for waitKey(1) the function will show a frame for at least 1 ms
    # only.
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
# Release everything if job is finished cap. release() and cv2. destroyAllWindows() are the methods to close video
# files or the capturing device, and destroy the window, which was created by the imshow method. ... The further dive
# into OpenCV for video processing is up to the reader.
capture.release()
out.release()
cv2.destroyAllWindows()
