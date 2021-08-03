"""
CLI Plugin for performing optimization.
"""
from argparse import ArgumentParser, Namespace
from typing import Dict
import itertools

from numpy.core.numeric import Inf
from firebase_admin import db
from cli_plugins.cli_plugin import CliPlugin
from library.metrics import calculate_loss, get_metrics
from library.firebase import initialize_app
from config import (
    get_config,
    get_latest_config,
    set_config_part,
    step_config,
    set_config,
    save_cloud_config,
)
import yaml
from config import get_config_part
from library.utils import flatten
import numpy as np
import hashlib

from sherlock import Sherlock


LOSS_THRESH = 0.01


class Optimize(CliPlugin):
    """
    CLI Plugin for performing optimization.
    """

    def __init__(self, parser: ArgumentParser):
        CliPlugin.__init__(self, parser)

        self._X = None
        self._knob_names = None
        self._config_decl_hash = None

    def _get_X(self):
        with open("./config_declaration.yml", "r") as f:
            config_declaration = yaml.load(f)

        bounds = [
            (
                p,
                self._get_resolution(p, config_declaration),
                self._get_property(p, "min", config_declaration, 0),
                self._get_property(p, "max", config_declaration, 100000),
            )
            for p in self._get_paths(config_declaration, "")
            if self._test_if_number_path(p, config_declaration)
        ]
        variables = [np.arange(min, max + r, r) for _, r, min, max in bounds]
        count = 1

        for var_list in variables:
            count *= len(var_list)

        return (
            [p for p, _, _, _ in bounds],
            np.array(list(itertools.product(*variables))),
        )

    def _get_paths(self, config_declaration: Dict[str, any], path: str):
        items = {
            ((path + "/" if path else "") + k): config_declaration[k]
            for k in config_declaration
            if "type" in config_declaration[k]
        }
        children = flatten(
            [
                self._get_paths(
                    config_declaration[k], ((path + "/" if path else "") + k)
                )
                for k in config_declaration
                if "type" not in config_declaration[k]
            ]
        )

        paths = [k for k in items]
        paths.extend(children)

        return paths

    def _test_if_number_path(self, path: str, config_declaration: Dict[str, any]):
        config_declar_part = get_config_part(path, config=config_declaration)
        var_type = config_declar_part["type"]

        return var_type in ["int32", "float"]

    def _get_resolution(self, path: str, config_declaration: Dict[str, any]):
        config_declar_part = get_config_part(path, config=config_declaration)
        var_type = config_declar_part["type"]

        if var_type == "int32":
            if "odd" in config_declar_part and config_declar_part["odd"]:
                return 2

            return 1

        if var_type == "float":
            return config_declar_part["std"]

        return 0

    def _get_property(
        self, path: str, prop: str, config_declaration: Dict[str, any], default_value,
    ):
        config_declar_part = get_config_part(path, config=config_declaration)

        return config_declar_part[prop] if prop in config_declar_part else default_value

    def _get_y(self, knob_names, X, idx):
        config = get_config()

        for k, x in zip(knob_names, X[idx, :]):
            set_config_part(k, config, x)

        set_config(config)
        metrics = get_metrics()

        true_positive = np.sum(np.array([m.true_positive for m in metrics]))
        false_positive = np.sum(np.array([m.false_positive for m in metrics]))
        # false_negative = np.sum(np.array([m.false_negative for m in metrics]))

        return np.array([true_positive, 1000000000 - false_positive])

    def _request_output(self, y, known_idx):
        sherlock_ref = db.reference("sherlock")
        hash_ref = sherlock_ref.child(self._config_decl_hash)

        for idx in known_idx:
            if np.sum(y[idx, :]) == 0:
                idx_ref = hash_ref.child(str(idx))

                if idx_ref.get() is not None:
                    y[idx, :] = np.array(idx_ref.get())
                else:
                    res = self._get_y(self._knob_names, self._X, idx)
                    idx_ref.set(res.tolist())
                    y[idx, :] = res

                print(y[idx, :])

    def execute(self, args: Namespace):
        initialize_app()

        with open("./config_declaration.yml", "rb") as f:
            self._config_decl_hash = hashlib.md5(f.read()).hexdigest()

        self._knob_names, self._X = self._get_X()
        y = np.zeros((self._X.shape[0], 2))

        sherlock = Sherlock(
            surrogate_type="rbfthin_plate-rbf_multiquadric-randomforest-gpy",
            request_output=self._request_output,
        )

        sherlock.fit(self._X).predict(self._X, y)

        # self._get_y(knob_names, X, y, 0)

        # prev_loss = Inf
        # loss = -Inf

        # initialize_app()
        # ref = db.reference("optimize")
        # continue_ref = ref.child("continue")

        # if continue_ref.get() is None:
        #     continue_ref.set(True)

        # # Allow optimization to be killed
        # while continue_ref.get():
        #     config, prev_loss, pulled_from_cloud = get_latest_config()
        #     if pulled_from_cloud:
        #         config = step_config(config)

        #     set_config(config)
        #     loss = calculate_loss(get_metrics())
        #     better = loss < prev_loss
        #     save_cloud_config(config, loss, better)

        #     should_stop = abs(prev_loss - loss) < LOSS_THRESH

        #     if better:
        #         prev_loss = loss

        #     if should_stop:
        #         break
