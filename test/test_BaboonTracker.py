import unittest
from baboon_tracking import BaboonTracker


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

    def test_successful_import(self):
        self.assertIsNotNone(BaboonTracker)
        tracker = BaboonTracker()
        self.assertIsNotNone(tracker)


if __name__ == "__main__":
    unittest.main()
