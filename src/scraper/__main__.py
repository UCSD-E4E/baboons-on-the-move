import sys
import cv2
import subprocess as sp
import numpy as np
import datetime, time, pytz, tzlocal
import os
import requests
from threading import Thread

is_not_headless = sys.argv.count('--headless') == 0

# local = tzlocal.get_localzone()
local = pytz.timezone('America/Los_Angeles')

threshold_pixel_diff = 30
threshold_diff_percent = .9
video_length = 10 * 60
sunset_url = 'https://api.sunrise-sunset.org/json?lat=32.7353&lng=-117.1490'

prev_thread = None

pipe = None
def captureImage():
    global pipe

    if pipe is None:
        pipe = sp.Popen(['ffmpeg', "-i", 'https://zssd-baboon.hls.camzonecdn.com/CamzoneStreams/zssd-baboon/Playlist.m3u8',
        "-loglevel", "quiet", # no text output
        "-an",   # disable audio
        "-f", "image2pipe",
        "-pix_fmt", "bgr24",
        "-vcodec", "rawvideo", "-"],
        stdin = sp.PIPE, stdout = sp.PIPE)

    raw_image = pipe.stdout.read(480*800*3) # read 480*800*3 bytes (= 1 frame)
    image =  np.fromstring(raw_image, dtype='uint8').reshape((480,800,3))

    return image

def uploadFile(file):
    global prev_thread

    # We don't want to back up too many uploads
    if prev_thread is not None:
        prev_thread.join()
    prev_thread = Thread(target = uploadFileSync, args = (file,))
    prev_thread.start()

def uploadFileSync(file):
    sp.call(['rclone', 'copy', file, 'aerial-baboons:SD_Zoo_Videos'], shell=False)

    os.remove(file)

def getSunrise(date):
    return getSunInfo(date, 'civil_twilight_begin')

def getSunset(date):
    # sunrise and sunset happen on different days in UTC.
    return getSunInfo(date, 'civil_twilight_end')

def getSunInfo(date, info):
    utc = date.astimezone(pytz.utc)

    json = requests.get(sunset_url + '&date=' + utc.strftime('%Y-%m-%d')).json()

    info = datetime.datetime.fromtimestamp(time.mktime(time.strptime(json['results'][info], '%I:%M:%S %p')))
    info = pytz.utc.localize(info).astimezone(local)
    info = info.replace(year=date.year, month=date.month, day=date.day)

    return info

def main():
    try:
        # Cleanup files from previous run
        output_files_to_delete = [f for f in os.listdir('.') if f.startswith('output')]
        [os.remove(f) for f in output_files_to_delete]

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = None

        now = datetime.datetime.now()

        sunrise = getSunrise(now)
        sunset = getSunset(now)

        night = True
        while(True):
            now = local.localize(datetime.datetime.now())

            if night and now >= sunrise:
                night = False

                # Get the next sunrise, for tomorrow
                sunrise = getSunrise(now + datetime.timedelta(days=1))
            if not night and now >= sunset:
                night = True

                if out is not None:
                    # Save the video to disk.
                    out.release()
                    out = None
                    uploadFile(file_name)

                # Get the next sunset, for tomorrow
                sunset = getSunset(now + datetime.timedelta(days=1))

            if night:
                print("Sleeping for 5 minutes")

                # Sleep for 5 minutes
                time.sleep(5 * 60)

                # No reason to capture when it's dark.  We can't see anything meaningful.
                continue

            # We do not currently have a video handle
            if out is None:
                file_name = 'output' + str(now.month) + '-' + str(now.day) + '-' + str(now.year) + 'T' + str(now.hour) + '-' + str(now.minute) + '.avi'
                out = cv2.VideoWriter(file_name,fourcc, 20.0, (800,480))
                start_time = time.time()

            image =  captureImage()
            
            if is_not_headless:
                # Display the resulting frame
                cv2.imshow('image', image)
            
            if time.time() - start_time > video_length:
                out.release()
                out = None
                uploadFile(file_name)

            if out is not None:
                # write the flipped frame
                out.write(image)

            if cv2.waitKey(5) == 27:
                break
    except KeyboardInterrupt:
        pass
    finally:
        if is_not_headless:
            cv2.destroyAllWindows()
        if out is not None:
            # When everything done, release the capture
            out.release()
            # We want to wait in case there are any uploads going.
            if prev_thread is not None:
                prev_thread.join()
            uploadFileSync(file_name)

if __name__ == '__main__':
    main()