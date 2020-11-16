"""
Contains a result of a stage execution.
"""


class StageResult:
    """
    Contains a result of a stage execution.
    """

    def __init__(self, continue_pipeline: bool, next_stage: bool):
        self.continue_pipeline = continue_pipeline
        self.next_stage = next_stage
