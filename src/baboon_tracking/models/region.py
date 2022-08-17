"""
Defines a region object.
"""
from typing import Tuple


class Region:
    """
    Defines a region object.
    """

    def __init__(
        self,
        rectange: Tuple[int, int, int, int],
        id_str: str = None,
        identity: int = None,
    ):
        self.rectangle = rectange
        self.id_str = id_str
        self.identity = identity
