from typing import Dict, Tuple
from genericpath import exists
import pickle
import yaml
import numpy as np
import hashlib
from firebase_admin import db

import third_party.pareto as pareto

from library.config import get_config_declaration, get_config_options
from library.firebase import get_dataset_ref


def get_design_space(
    video_file: str,
    enable_tracking: bool,
    enable_persist: bool,
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

    current_idx_ref = persist_ref.child("current_idx")
    known_idx_ref = persist_ref.child("known_idx")

    updated_cache = False
    known_idx = [idx for idx in (known_idx_ref.get() or []) if idx is not None]
    for idx in known_idx:
        cache_key = (
            config_hash,
            video_file,
            enable_tracking,
            enable_persist,
            idx,
        )

        if cache_key in cache:
            recall, precision, f1 = cache[cache_key]
        else:
            idx_ref = persist_ref.child(str(idx))
            recall, precision, f1 = idx_ref.get()
            cache[cache_key] = (recall, precision, f1)
            updated_cache = True

        y[idx, :] = np.array([recall, precision, f1])

    if updated_cache:
        with open(cache_path, "wb") as f:
            pickle.dump(cache, f)

    current_idx = [idx for idx in (current_idx_ref.get() or []) if idx is not None]
    return X, y, current_idx, known_idx


def get_pareto_front(video_file: str, enable_tracking: bool, enable_persist: bool):
    _, y, current_idx, known_idx = get_design_space(
        video_file, enable_tracking, enable_persist
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
