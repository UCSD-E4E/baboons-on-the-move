"""
Handles reading from /config.yml
"""

import os
import yaml


def get_config() -> any:
    """
    Load the config.yml file in the root of the repository.
    """
    with open(os.path.realpath("./config.yml"), "r") as stream:
        try:
            return yaml.safe_load(stream)

        except yaml.YAMLError as exc:
            print(exc)
