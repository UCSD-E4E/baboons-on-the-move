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

        runtime_config = {"display": False, "save": False}

        for file in files:
            output_file = join(baseline_folder, splitext(basename(file))[0] + ".csv")
            baboon_tracker = BaboonTracker(file, runtime_config=runtime_config)
            baboons_mixin: BaboonsMixin = baboon_tracker.get(BaboonsMixin)

            with open(output_file, "w", encoding="utf8") as f:
                should_continue = True
                frame_counter = 1
                while should_continue:
                    should_continue = baboon_tracker.step().continue_pipeline

                    if baboons_mixin.baboons is not None:
                        for baboon in baboons_mixin.baboons:
                            x1, y1, x2, y2 = baboon.rectangle
                            f.write(f"{x1}, {y1}, {x2}, {y2}, {frame_counter}\n")

                    frame_counter += 1
