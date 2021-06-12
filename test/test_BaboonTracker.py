from os import listdir
from os.path import basename, join, isfile, splitext
from typing import List
import unittest

from baboon_tracking import BaboonTracker
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin


class TestBaboonTracker(unittest.TestCase):
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

    def test_motion_detection(self):
        root = "./data/tests"
        files = [join("tests", d) for d in listdir(root) if isfile(join(root, d))]

        baseline_folder = ""
        with open("baseline.txt", "r") as f:
            baseline_folder = "./data/tests/baselines/" + f.readline()

        runtime_config = {"display": False}

        print("")
        for file in files:
            print('Testing "' + file + '"')

            baseline_file = join(baseline_folder, splitext(basename(file))[0] + ".csv")
            baboon_tracker = BaboonTracker(
                input_file=file, runtime_config=runtime_config
            )
            baboons_mixin: BaboonsMixin = baboon_tracker.get(BaboonsMixin)

            baboons: List[str] = []
            with open(baseline_file, "r") as f:
                baboons = [[p.strip() for p in l.split(",")] for l in f.readlines()]

            should_continue = True
            frame_counter = 1
            while should_continue:
                should_continue = baboon_tracker.step().continue_pipeline

                if baboons_mixin.baboons is not None:
                    curr_frame_baboons = [
                        (float(x1), float(y1), float(x2), float(y2))
                        for x1, y1, x2, y2, frame in baboons
                        if int(frame) == frame_counter
                    ]

                    new_found_baboons = [
                        (b.rectangle[0], b.rectangle[1], b.rectangle[2], b.rectangle[3])
                        for b in baboons_mixin.baboons
                    ]

                    self.assertListEqual(new_found_baboons, curr_frame_baboons)

                frame_counter += 1


if __name__ == "__main__":
    unittest.main()
