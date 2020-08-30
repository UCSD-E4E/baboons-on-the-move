def chart():
    """
    Generates a chart representing the baboon tracking algorithm.
    """

    from baboon_tracking import BaboonTracker  # pylint: disable=import-outside-toplevel

    BaboonTracker().flowchart().show()
