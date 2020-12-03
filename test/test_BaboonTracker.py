import baboon_tracking as bt
from baboon_tracking import BaboonTracker
import multiprocessing
import unittest


class TestBaboonTracker(unittest.TestCase):
    def setUp(self):
        self.config = {
            "input": "./data/input.mp4",
            "output": "./output/output.mp4",
            "display": {"width": 1600, "height": 900},
        }

    def test_sample_1(self):
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_sample_2(self):
        self.assertIsNone(None)
        self.assertIsNotNone(1)


if __name__ == "__main__":
    unittest.main()
