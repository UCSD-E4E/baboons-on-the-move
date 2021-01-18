"""
Mixin for returning blob images.
"""
from baboon_tracking.models.frame import Frame


class BlobImageMixin:
    """
    Mixin for returning blob images.
    """

    def __init__(self):
        self.blob_image: Frame = None
