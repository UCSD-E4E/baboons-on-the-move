"""
Module for calculating metrics.
"""
import numpy as np

from baboon_tracking import BaboonTracker
from baboon_tracking.mixins.baboons_mixin import BaboonsMixin
from library.labeled_data import get_centroids_from_xml
from library.region import check_if_same_region


def get_metrics():
    """
    Gets the metrics for the specified video.
    """
    print("testing on input")
    baboon_labels = get_centroids_from_xml("./data/input.xml")

    baboon_tracker = BaboonTracker(input_file="input.mp4")
    print("tracker opened")
    baboons_mixin: BaboonsMixin = baboon_tracker.get(BaboonsMixin)

    should_continue = True
    frame_counter = 0
    metrics = []
    while should_continue:
        print("frame: " + str(frame_counter))

        true_positive = 0
        false_positive = 0

        should_continue = baboon_tracker.step().continue_pipeline
        new_found_baboons = []
        labeled_baboons = []
        if baboons_mixin.baboons is not None:
            new_found_baboons = [
                (b.centroid[0], b.centroid[1], b.diameter)
                for b in baboons_mixin.baboons
            ]
        if frame_counter in baboon_labels:
            labeled_baboons = baboon_labels[frame_counter]

            matched_baboons = []
            for new_found_baboon in new_found_baboons:

                baboon_in_labels = [
                    lb
                    for lb in labeled_baboons
                    if check_if_same_region(lb, new_found_baboon)
                ]

                matched_baboons.extend(baboon_in_labels)
                if baboon_in_labels:
                    true_positive += 1
                else:
                    false_positive += 1

                labeled_baboons = [
                    lb for lb in labeled_baboons if lb not in baboon_in_labels
                ]

            false_negative = len(labeled_baboons)

            metrics.append((true_positive, false_negative, false_positive))

            # exit()

            # found_mask = create_mask(new_found_baboons)
            # label_mask = create_mask(labeled_baboons)
            # metrics.append(categorize_observations(found_mask, label_mask))
        else:
            should_continue = False

        frame_counter += 1

    return np.array(metrics)
