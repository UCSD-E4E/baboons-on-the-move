import argparse
from typing import Callable, List


def str2bool(value):
    """
    Sets up a command line argument that can be converted to bool.
    """
    if isinstance(value, bool):
        return value
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if value.lower() in ("no", "false", "f", "n", "0"):
        return False

    raise argparse.ArgumentTypeError("Boolen value expected.")


def str2factory(*factories: List[Callable]):
    """
    Sets up a command line argument that can be converted to a stage factory.
    """

    def get_name(factory: Callable):
        name_parts = factory.__name__.split("_")
        return "".join([n.capitalize() for n in name_parts if n != "factory"])

    def internal(value: str):
        factory_names = {get_name(f): f for f in factories}

        if value in factory_names:
            return factory_names[value]

        raise argparse.ArgumentTypeError(
            f"{', '.join(factory_names)} value expected, recieved '{value}' instead."
        )

    return internal
