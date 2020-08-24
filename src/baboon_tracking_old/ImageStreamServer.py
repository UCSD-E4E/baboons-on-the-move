import io
import numpy as np
import pika
import cv2


class ImageStreamServer:
    def __init__(self, host, port):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="imshow")

    def imshow(self, img):
        compressed_img = io.BytesIO()
        np.savez_compressed(compressed_img, img)
        compressed_img.seek(0)

        self.channel.basic_publish(
            exchange="", routing_key="imshow", body=compressed_img.read()
        )

    def close(self):
        self.connection.close()
