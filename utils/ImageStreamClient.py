import cv2
import io
import numpy as np;
import pika
import matplotlib.pyplot as plt

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='imshow')

def callback(ch, method, properties, body):
    compressed_img = io.BytesIO()
    compressed_img.write(body)
    compressed_img.seek(0)
    img = np.load(compressed_img)['arr_0']

    cv2.imshow('Remote', img)
    cv2.waitKey()

channel.basic_consume(
    queue='imshow',
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()
