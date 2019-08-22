import baboon_tracking as bt
import baboon_tracking.BaboonTracker as BaboonTracker
import multiprocessing
import unittest

class TestBaboonTracker(unittest.TestCase):

    def setUp(self):
        self.config = {
                'input': './data/input.mp4',
                'output': './output/output.mp4',
                'display': {'width': 1600, 'height': 900},
                'history_frames': 10, 'registration': {
                    'max_features': 500,
                    'good_match_percent': 0.15}
                }

    def test_none_constructor(self):
        tracker = BaboonTracker(config=self.config)
        self.assertIsNotNone(tracker)

    def test_yamlconfig_constructor(self):
        tracker = BaboonTracker(config=self.config)
        self.assertIsNotNone(tracker)

    def test_kwargs_constructor(self):
         cpus = multiprocessing.cpu_count()
         pool = multiprocessing.Pool(processes=cpus)

         registration = bt.registration.ORB_RANSAC_Registration(self.config)
         fg_extraction = bt.foreground_extraction.VariableBackgroundSub_ForegroundExtraction(self.config)

         tracker = bt.BaboonTracker(config=self.config, registration=registration, foreground_extraction=fg_extraction, pool=pool)

         self.assertIsNotNone(tracker)
         self.assertEqual(pool, tracker.pool)
         self.assertEqual(registration, tracker.registration)
         self.assertEqual(fg_extraction, tracker.foreground_extraction)


if __name__ == '__main__':
    unittest.main()

