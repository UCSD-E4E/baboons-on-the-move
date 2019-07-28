import io
import numpy as np;
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel

channel.queue_declare(queue='imshow')

def imshow(img):
    compressed_img = io.BytesIO()
    np.savez_compressed(compressed_img, img)
    compressed_img.seek(0)

    channel.basic_publish(
        exchange = '',
        routing_key='imshow',
        body=compressed_ing.read()
    )

def close():
    connection.close()