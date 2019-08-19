import baboon_tracking.ImageStreamServer as ImageStreamServer
import unittest

class TestImageStreamTracker(unittest.TestCase):

    def test_1(self):
        self.assertTrue(True)

    def test_2(self):
        self.assertFalse(False)

    def test_exists(self):
        tracker = ImageStreamServer('localhost', '5672')
        self.assertIsNotNone(tracker)

if __name__ == '__main__':
    unittest.main()

