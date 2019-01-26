import sys
import cv2
import subprocess as sp
import numpy
import datetime

threshold = 10

def main():
    pipe = sp.Popen(['ffmpeg', "-i", 'https://zssd-baboon.hls.camzonecdn.com/CamzoneStreams/zssd-baboon/Playlist.m3u8',
           "-loglevel", "quiet", # no text output
           "-an",   # disable audio
           "-f", "image2pipe",
           "-pix_fmt", "bgr24",
           "-vcodec", "rawvideo", "-"],
           stdin = sp.PIPE, stdout = sp.PIPE)

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    now = datetime.datetime.now()
    out = cv2.VideoWriter('output' + str(now.day) + '-' + str(now.month) + '-' + str(now.year) + 'T' + str(now.hour) + '-' + str(now.minute) + '.avi',fourcc, 20.0, (800,480))

    while(True):
        raw_image = pipe.stdout.read(480*800*3) # read 432*240*3 bytes (= 1 frame)
        image =  numpy.fromstring(raw_image, dtype='uint8').reshape((480,800,3))

        # Display the resulting frame
        cv2.imshow('Baboon', image)

        # write the flipped frame
        out.write(image)

        if cv2.waitKey(5) == 27:
            break

    # When everything done, release the capture
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()