"""
Baseline generator for the baboon tracker.
"""

from os import listdir
from os.path import basename, isfile, join, splitext

from baboon_tracking.baboon_tracker import BaboonTracker
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin


class BaselineBaboonTracker:
    """
    Baseline generator for the baboon tracker.
    """

    def execute(self, baseline_folder: str):
        """
        Executes the baseline generator for the baboon tracker.
        """
        root = "./data/tests"
        files = [join("tests", d) for d in listdir(root) if isfile(join(root, d))]

        for file in files:
            output_file = join(baseline_folder, splitext(basename(file))[0] + ".csv")
            baboon_tracker = BaboonTracker(input_file=file)
            baboons_mixin: BaboonsMixin = baboon_tracker.get(BaboonsMixin)

            with open(output_file, "w") as f:
                should_continue = True
                frame_counter = 1
                while should_continue:
                    should_continue = baboon_tracker.step().continue_pipeline

                    if baboons_mixin.baboons is not None:
                        for baboon in baboons_mixin.baboons:
                            centroid_x, centroid_y = baboon.centroid
                            f.write(
                                "{0}, {1}, {2}, {3}\n".format(
                                    centroid_x,
                                    centroid_y,
                                    baboon.diameter,
                                    frame_counter,
                                )
                            )

                    frame_counter += 1
