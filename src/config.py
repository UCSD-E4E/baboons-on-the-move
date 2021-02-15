"""
Handles reading from /config.yml
"""

import os
from datetime import datetime
from random import gauss
from typing import Dict

import firebase_admin
from firebase_admin import credentials, db
from numpy.core.numeric import Inf

import yaml


CONFIG_STORE = None


def set_config(config: Dict):
    global CONFIG_STORE
    CONFIG_STORE = config


def get_config() -> Dict:
    """
    Load the config.yml file in the root of the repository.
    """
    if CONFIG_STORE is None:
        with open(os.path.realpath("./config.yml"), "r") as stream:
            try:
                return yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                print(exc)
    else:
        return CONFIG_STORE


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
    with open(os.path.realpath("./config_declaration.yml"), "r") as stream:
        declaration = yaml.safe_load(stream)

    _update_config(config, declaration)

    return config


def get_latest_config() -> Dict:
    cred = credentials.Certificate("decrypted/firebase-key.json")
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://baboon-cli-1598770091002-default-rtdb.firebaseio.com/"
        },
    )

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
    cred = credentials.Certificate("decrypted/firebase-key.json")
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://baboon-cli-1598770091002-default-rtdb.firebaseio.com/"
        },
    )

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
