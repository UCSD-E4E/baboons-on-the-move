from typing import Dict, List, Set, Tuple
from genericpath import exists
import pickle
import yaml
import numpy as np
import hashlib
from firebase_admin import db
from library.dataset import get_dataset_path

import third_party.pareto as pareto
import cv2

from library.config import get_config_declaration, get_config_options
from library.firebase import get_dataset_ref, initialize_app


class DesignSpaceCache:
    def __init__(
        self,
        value_cache: Dict[
            Tuple[str, str, str, bool, bool, int], Tuple[float, float, float]
        ] = {},
        known_idx_cache: Dict[str, List[int]] = {},
        current_idx_cache: Dict[str, List[int]] = {},
        requested_idx_cache: Dict[str, Set[int]] = {},
    ):
        self._value_cache = value_cache
        self._known_idx_cache = known_idx_cache
        self._current_idx_cache = current_idx_cache
        self._updated_cache = False

    def check_value(self, cache_key: Tuple[str, str, bool, bool, int]):
        return cache_key in self._value_cache

    def get_value(self, cache_key: Tuple[str, str, bool, bool, int]):
        if cache_key in self._value_cache:
            return self._value_cache[cache_key]
        else:
            raise f"{cache_key} not found in cache."

    def set_value(
        self,
        cache_key: Tuple[str, str, bool, bool, int],
        recall: float,
        precision: float,
        f1: float,
    ):
        self._value_cache[cache_key] = (recall, precision, f1)
        self._updated_cache = True

    def _compare_list(self, list1: List[int], list2: List[int]):
        return set(list1) == set(list2)

    def set_known_idx(self, video_file: str, known_idx: List[int]):
        if video_file not in self._known_idx_cache or not self._compare_list(
            self._known_idx_cache[video_file], known_idx
        ):
            self._known_idx_cache[video_file] = known_idx
            self._updated_cache = True

    def get_known_idx(self, video_file: str):
        return self._known_idx_cache[video_file]

    def set_current_idx(self, video_file: str, current_idx: List[int]):
        if video_file not in self._current_idx_cache or not self._compare_list(
            self._current_idx_cache[video_file], current_idx
        ):
            self._current_idx_cache[video_file] = current_idx
            self._updated_cache = True

    def get_current_idx(self, video_file: str):
        return self._current_idx_cache[video_file]

    def get_cache_changed(self):
        return self._updated_cache


def get_design_space(
    video_file: str,
    enable_tracking: bool,
    enable_persist: bool,
    max_width: int = None,
    max_height: int = None,
    disable_network=False,
):
    if max_width is None or max_height is None:
        dataset_path = get_dataset_path(video_file)

        img = cv2.imread(f"{dataset_path}/img/000001.jpg")
        frame_height, frame_width, _ = img.shape

        max_width = max_width or frame_width
        max_height = max_height or frame_height

    if not disable_network:
        initialize_app()

    cache_path = "./output/plot_cache.pickle"
    cache: DesignSpaceCache = None
    if exists(cache_path):
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
    else:
        cache = DesignSpaceCache()

    with open("./config_declaration.yml", "r", encoding="utf8") as f:
        config_declaration = get_config_declaration("", yaml.safe_load(f))
        f.seek(0)

    config_options = [
        (k, get_config_options(i), i["type"])
        for k, i in config_declaration.items()
        if "skip_learn" not in i or not i["skip_learn"]
    ]
    X = np.array(np.meshgrid(*[c for _, c, _ in config_options])).T.reshape(
        -1, len(config_options)
    )
    y = np.zeros((X.shape[0], 3))

    with open("./config_declaration.yml", "rb") as f:
        config_hash = hashlib.md5(f.read()).hexdigest()

    if not disable_network:
        sherlock_ref = db.reference("sherlock")

        video_file_ref = get_dataset_ref(video_file, sherlock_ref)
        config_declaration_ref = video_file_ref.child(config_hash)

        if enable_tracking:
            tracking_ref = config_declaration_ref.child("tracking_enabled")
        else:
            tracking_ref = config_declaration_ref.child("tracking_disabled")

        if enable_persist:
            persist_ref = tracking_ref.child("persist_enabled")
        else:
            persist_ref = tracking_ref.child("persist_disabled")

        max_width_ref = persist_ref.child(f"max_width_{max_width}")
        max_height_ref = max_width_ref.child(f"max_height_{max_height}")

        known_idx_ref = max_height_ref.child("known_idx")

        known_idx = [idx for idx in (known_idx_ref.get() or []) if idx is not None]
        cache.set_known_idx(video_file, known_idx)
    else:
        known_idx = cache.get_known_idx(video_file)

    for idx in known_idx:
        cache_key = (
            config_hash,
            video_file,
            enable_tracking,
            enable_persist,
            max_width,
            max_height,
            idx,
        )

        if cache.check_value(cache_key):
            recall, precision, f1 = cache.get_value(cache_key)
        elif not disable_network:
            idx_ref = max_height_ref.child(str(idx))
            recall, precision, f1 = idx_ref.get()
            cache.set_value(cache_key, recall, precision, f1)
        else:
            raise f"{cache_key} is not found in cache.  This likely means an incomplete cache.  Please run with network and try again."

        y[idx, :] = np.array([recall, precision, f1])

    if not disable_network:
        current_idx_ref = max_height_ref.child("current_idx")
        current_idx = [idx for idx in (current_idx_ref.get() or []) if idx is not None]
        cache.set_current_idx(video_file, current_idx)
    else:
        current_idx = cache.get_current_idx(video_file)

    if cache.get_cache_changed():
        with open(cache_path, "wb") as f:
            pickle.dump(cache, f)

    return X, y, current_idx, known_idx


def get_pareto_front(
    video_file: str,
    enable_tracking: bool,
    enable_persist: bool,
    max_width: int = None,
    max_height: int = None,
    disable_network=False,
):
    _, y, current_idx, known_idx = get_design_space(
        video_file,
        enable_tracking,
        enable_persist,
        max_width=max_width,
        max_height=max_height,
        disable_network=disable_network,
    )

    current_idx = np.array(current_idx)
    current_outputs = np.array(y[current_idx, :])

    known_idx = np.array(known_idx)

    ypredict, ypredict_idx, _ = approximate_pareto(current_outputs)
    ypredict_idx = known_idx[ypredict_idx].flatten()

    return ypredict, ypredict_idx


# From github.com/KastnerRG/sherlock/utils
def compute_scores(y, rows, margin=0):
    ndrange = np.ptp(y, axis=0) * margin
    total_sum = np.sum(y, axis=0)
    nrows = y.shape[0]
    scores = np.empty(len(rows), dtype=float)
    for i, r in enumerate(rows):
        scores[i] = np.sum(r * nrows - total_sum + ndrange * (nrows - 1))
    return scores


def approximate_pareto(y, epsilons=None, margin=0):
    """
    Uses pareto.py from https://github.com/matthewjwoodruff/pareto.py
    Returns the same data as prpt.
    """
    tagalongs = np.array(
        pareto.eps_sort(y, epsilons=epsilons, maximize_all=True, attribution=True)
    )
    pareto_solutions = tagalongs[:, : y.shape[1]]
    pareto_idx = tagalongs[:, y.shape[1] + 1].astype(int)
    if margin > 0:
        miny = np.min(y, axis=0)
        ptp = pareto_solutions - miny
        margin = ptp * margin
        pareto_idx = range(y.shape[0])
        for s, m in zip(pareto_solutions, margin):
            pareto_idx = np.intersect1d(
                pareto_idx, np.where(np.any(y >= s - m, axis=1))[0], assume_unique=True
            )
        pareto_solutions = y[pareto_idx, :]
    pareto_scores = compute_scores(y, pareto_solutions)
    return pareto_solutions, pareto_idx, pareto_scores
