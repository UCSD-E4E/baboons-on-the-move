from argparse import ArgumentParser, Namespace
import hashlib
from firebase_admin import db
import yaml
from cli_plugins.cli_plugin import CliPlugin
from library.dataset import get_dataset_path
from library.firebase import initialize_app
from typing import Dict, Any, Tuple
import numpy as np
import matplotlib.pyplot as plt
from sherlock.utils import approximate_pareto
from os.path import exists
import pickle


class Plot(CliPlugin):
    VIDEO_FILES = [
        "VISO/car/003",
        "VISO/car/004",
        "VISO/car/005",
        "VISO/car/006",
        "VISO/car/007",
        "VISO/car/008",
        "VISO/car/009",
    ]

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

    def _get_config_options(self, config_declaration: Dict[str, Any]):
        type_value = None
        if config_declaration["type"] == "int32":
            type_value = np.int32
        elif config_declaration["type"] == "float":
            type_value = np.float32

        if "step" in config_declaration:
            step = config_declaration["step"]
        else:
            step = 1

        if "min" in config_declaration:
            min_value = config_declaration["min"]
        else:
            min_value = 0

        if "max" in config_declaration:
            max_value = config_declaration["max"]
        else:
            max_value = 100

        if "odd" in config_declaration:
            is_odd = config_declaration["odd"]
        else:
            is_odd = False

        if is_odd:
            min_value -= 1
            max_value = max_value / 2

        values = np.arange(min_value, max_value, step=step, dtype=type_value)
        if is_odd:
            values = values * 2 + 1

        return values

    def _extend(self, target: Dict[str, Any], source: Dict[str, Any]):
        for key, value in source.items():
            target[key] = value

        return target

    def _get_config_declaration(self, root: str, config_declaration: Dict[str, Any]):
        leaf_nodes = {}

        for key, value in config_declaration.items():
            if isinstance(value, dict):
                self._extend(
                    leaf_nodes, self._get_config_declaration(f"{root}/{key}", value)
                )
                continue

        if not leaf_nodes.keys():
            leaf_nodes[root] = config_declaration

        return leaf_nodes

    def _get_results(
        self, video_file: str, enable_tracking: bool, enable_persist: bool
    ):
        cache_path = "./output/plot_cache.pickle"
        cache: Dict[
            Tuple[str, int, str, bool, bool, int], Tuple[float, float, float]
        ] = None
        if exists(cache_path):
            with open(cache_path, "rb") as f:
                cache = pickle.load(f)
        else:
            cache = {}

        with open("./config_declaration.yml", "r", encoding="utf8") as f:
            config_declaration = self._get_config_declaration("", yaml.safe_load(f))
            f.seek(0)

        config_options = [
            (k, self._get_config_options(i), i["type"])
            for k, i in config_declaration.items()
            if "skip_learn" not in i or not i["skip_learn"]
        ]
        X = np.array(np.meshgrid(*[c for _, c, _ in config_options])).T.reshape(
            -1, len(config_options)
        )
        y = np.zeros((X.shape[0], 3))

        with open("./config_declaration.yml", "rb") as f:
            config_hash = hashlib.md5(f.read()).hexdigest()

        sherlock_ref = db.reference("sherlock")
        dataset_path = get_dataset_path(video_file)
        video_name = dataset_path.split("/")[-1]

        video_name_ref = sherlock_ref.child(video_name)
        config_declaration_ref = video_name_ref.child(config_hash)

        if enable_tracking:
            tracking_ref = config_declaration_ref.child("tracking_enabled")
        else:
            tracking_ref = config_declaration_ref.child("tracking_disabled")

        if enable_persist:
            persist_ref = tracking_ref.child("persist_enabled")
        else:
            persist_ref = tracking_ref.child("persist_disabled")

        frame_count_ref = persist_ref.child("20")
        known_idx_ref = frame_count_ref.child("known_idx")

        updated_cache = False
        known_idx = known_idx_ref.get()
        for idx in known_idx:
            cache_key = (
                config_hash,
                20,
                video_name,
                enable_tracking,
                enable_persist,
                idx,
            )

            if cache_key in cache:
                recall, precision, f1 = cache[cache_key]
            else:
                idx_ref = frame_count_ref.child(str(idx))
                recall, precision, f1 = idx_ref.get()
                cache[cache_key] = (recall, precision, f1)
                updated_cache = True

            y[idx, :] = np.array([recall, precision, f1])

        if updated_cache:
            with open(cache_path, "wb") as f:
                pickle.dump(cache, f)

        known_outputs = y[known_idx, :]
        # known_X = X[known_idx, :]
        kpareto, kpareto_idx, _ = approximate_pareto(known_outputs)

        plt.scatter(
            known_outputs[:, 0],
            known_outputs[:, 1],
            c="blue",
            marker="^",
            label="Sampled designs",
        )
        plt.scatter(
            kpareto[:, 0], kpareto[:, 1], c="red", label="Pareto optimal designs"
        )
        plt.legend(bbox_to_anchor=(1.05, 1.05))
        # plt.set_xlim(y[:, 0].min(), y[:, 0].max())
        # plt.set_ylim(y[:, 1].min(), y[:, 1].max())

        plt.show()

    def execute(self, args: Namespace):
        initialize_app()

        for video_file in Plot.VIDEO_FILES:
            self._get_results(video_file, True, False)
            # self._get_results(video_file, False, True)
