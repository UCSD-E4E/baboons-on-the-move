"""
Defines a baboon object.
"""
from typing import Tuple


class Baboon:
    """
    Defines a baboon object.
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
