import baboon_tracking.BaboonTracker as BaboonTracker
import unittest

class TestBaboonTracker(unittest.TestCase):

    def test_1(self):
        self.assertTrue(True)

    def test_2(self):
        self.assertFalse(False)

    def test_exists(self):
        tracker = BaboonTracker(None)
        self.assertIsNotNone(tracker)

if __name__ == '__main__':
    unittest.main()

