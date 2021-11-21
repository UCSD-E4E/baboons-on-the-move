"""
Handles reading from /config.yml
"""

import os
from datetime import datetime
from random import gauss
from typing import Dict, Tuple

from firebase_admin import db
from numpy.core.numeric import Inf
import yaml

from library.firebase import initialize_app


CONFIG_STORE = None


def set_config(config: Dict):
    """
    Updates the config store with the specified config.
    """

    # pylint: disable=global-statement
    global CONFIG_STORE
    CONFIG_STORE = config


def get_config() -> Dict:
    """
    Load the config.yml file in the root of the repository.
    """
    if CONFIG_STORE is None:
        with open(os.path.realpath("./config.yml"), "r", encoding="utf8") as stream:
            try:
                return yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                print(exc)
    else:
        return CONFIG_STORE

    return {}


def get_config_part(key: str, config=None) -> Dict:
    """
    Gets the config part at the specified key.
    """
    if config is None:
        config = get_config()

    key_parts = key.split("/")

    key_curr_config = config
    for key_part in key_parts:
        key_curr_config = key_curr_config[key_part]

    return key_curr_config


def set_config_part(key: str, config: Dict, value: any):
    key_parts = key.split("/")
    last_key_part = key_parts[-1]
    key_parts = key_parts[:-1]

    key_curr_config = config
    for key_part in key_parts:
        key_curr_config = key_curr_config[key_part]

    key_curr_config[last_key_part] = value


def _update_config(config: Dict, declaration: Dict):
    for key, value in declaration.items():
        if "type" in value:
            if "skip_learn" in value and value["skip_learn"]:
                continue

            num = float(config[key]) + gauss(0, float(value["std"]))

            if "min" in value:
                num = max(float(value["min"]), num)
            if "max" in value:
                num = min(float(value["max"]), num)

            if value["type"] == "int32":
                num = round(num)

                if "odd" in value and value["odd"] and num % 2 == 0:
                    num = config[key]

            config[key] = num
        else:
            _update_config(config[key], value)


def step_config(config: Dict) -> Dict:
    """
    Steps the config file once.
    """
    with open(
        os.path.realpath("./config_declaration.yml"), "r", encoding="utf8"
    ) as stream:
        declaration = yaml.safe_load(stream)

    _update_config(config, declaration)

    return config


def get_latest_config() -> Tuple[Dict, float, bool]:
    """
    Gets the latest config from either the cloud or from the file system if the cloud doesn't have any results.
    """
    initialize_app()

    ref = db.reference("optimize")
    video_ref = ref.child("input")
    latest_ref = video_ref.child("latest")
    losses_ref = video_ref.child("losses")

    latest_value = latest_ref.get()

    if latest_value:
        config_ref = video_ref.child(latest_value)
        current_loss = losses_ref.child(latest_value)

        return_value = (config_ref.get(), current_loss.get(), True)
    else:
        return_value = (get_config(), Inf, False)

    return return_value


def save_cloud_config(config: Dict, loss: float, set_latest: bool):
    """
    Saves the the specified config file witth the specified loss to the cloud.
    """
    initialize_app()

    time = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    ref = db.reference("optimize")
    video_ref = ref.child("input")
    latest_ref = video_ref.child("latest")
    losses_ref = video_ref.child("losses")

    current_config_ref = video_ref.child(time)
    current_config_ref.set(config)

    current_loss_ref = losses_ref.child(time)
    current_loss_ref.set(loss)

    if set_latest:
        latest_ref.set(time)


def save_config(config: Dict):
    """
    Updates the config.yaml file with the specified config.
    """
    with open("./config.yml", "w", encoding="utf8") as f:
        yaml.dump(config, f)
