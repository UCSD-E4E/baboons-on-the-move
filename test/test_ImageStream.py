import baboon_tracking.ImageStreamServer as ImageStreamServer
import docker
import unittest
import time


class TestImageStream(unittest.TestCase):
    def setUp(self):
        self.client = docker.from_env()
        try:
            self.rabbit = self.client.containers.get("rabbitmq")
            self.started_rabbit = False
        except docker.errors.NotFound:
            self.rabbit = self.client.containers.run(
                image="rabbitmq:3.8.0-beta.5",
                name="rabbitmq",
                ports={"5672": 5672, "15672": 15672},
                detach=True,
            )
            # wait 10 seconds for docker container to set up
            time.sleep(10)
            self.started_rabbit = True

    def test_imagestreamserver_up(self):
        tracker = ImageStreamServer("localhost", "5672")
        self.assertIsNotNone(tracker)

    # TODO Implement tests
    def test_imagestreamclient_up(self):
        pass

    def test_imagestreamserver_send(self):
        pass

    def test_imagestreamclient_receive(self):
        pass

    def tearDown(self):
        if self.started_rabbit:
            self.rabbit.remove(force=True)


if __name__ == "__main__":
    unittest.main()
