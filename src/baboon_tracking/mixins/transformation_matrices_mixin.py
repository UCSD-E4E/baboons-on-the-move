"""
Mixin for returning tranformation matrices.
"""


class TransformationMatricesMixin:
    """
    Mixin for returning tranformation matrices.
    """

    def __init__(self):
        self.transformation_matrices = []
        self.current_frame_transformation = None
