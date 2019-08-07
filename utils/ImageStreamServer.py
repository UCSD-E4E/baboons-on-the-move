import io
import numpy as np;
import pika
import cv2

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='imshow')

def imshow(img):
    global channel

    compressed_img = io.BytesIO()
    np.savez_compressed(compressed_img, img)
    compressed_img.seek(0)

    channel.basic_publish(
        exchange = '',
        routing_key='imshow',
        body=compressed_img.read()
    )

def close():
    connection.close()

# TEST RUN

cap = cv2.VideoCapture("../data/input.mp4")

while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        framenum = framenum + 1
        imshow(gray)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Break the loop
    else:
        break

# When everything done, release the video capture object
cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()
