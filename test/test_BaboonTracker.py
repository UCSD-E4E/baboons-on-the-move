import baboon_tracking as bt
import baboon_tracking.BaboonTracker as BaboonTracker
import multiprocessing
import unittest

class TestBaboonTracker(unittest.TestCase):

    def test_none_constructor(self):
        tracker = BaboonTracker()
        self.assertIsNotNone(tracker)

    def test_yamlconfig_constructor(self):
        config = None
        tracker = BaboonTracker(config=config)

        # TODO IMPLEMENT YAML CONFIG PARSING

        self.assertIsNotNone(tracker)

    def test_kwargs_constructor(self):
         cpus = multiprocessing.cpu_count()
         pool = multiprocessing.Pool(processes=cpus)

         registration = bt.registration.ORB_RANSAC_Registration(None)
         fg_extraction = bt.foreground_extraction.VariableBackgroundSub_ForegroundExtraction(None)

         tracker = bt.BaboonTracker(registration=registration, foreground_extraction=fg_extraction, pool=pool)

         self.assertIsNotNone(tracker)
         self.assertEqual(pool, tracker.pool)
         self.assertEqual(registration, tracker.registration)
         self.assertEqual(fg_extraction, tracker.foreground_extraction)


if __name__ == '__main__':
    unittest.main()

