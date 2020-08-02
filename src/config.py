import os
import yaml


def get_config() -> any:
    with open(os.path.realpath("./config.yml"), "r") as stream:
        try:
            return yaml.safe_load(stream)

        except yaml.YAMLError as exc:
            print(exc)
            return

