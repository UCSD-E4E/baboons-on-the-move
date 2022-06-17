from argparse import ArgumentParser, Namespace
import hashlib
import math
from firebase_admin import db
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.figure import Figure
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
from os import makedirs


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

    def _get_design_space(
        self, video_name: str, enable_tracking: bool, enable_persist: bool
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
        # known_idx_ref = frame_count_ref.child("current_idx")

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
        ypredict, ypredict_idx, _ = approximate_pareto(known_outputs)

        return y, known_outputs, known_idx, ypredict, ypredict_idx, frame_count_ref

    def _get_results(
        self,
        video_file: str,
        enable_tracking: bool,
        enable_persist: bool,
        reference_video_name: str,
        ax: Axes,
    ):
        if reference_video_name:
            reference_video_idx = Plot.VIDEO_FILES.index(
                f"VISO/car/{reference_video_name}"
            )

        dataset_path = get_dataset_path(video_file)
        video_name = dataset_path.split("/")[-1]
        video_idx = Plot.VIDEO_FILES.index(f"VISO/car/{video_name}")

        (
            y,
            known_outputs,
            known_idx,
            ypredict,
            ypredict_idx,
            storage_ref,
        ) = self._get_design_space(video_name, enable_tracking, enable_persist)

        ax.scatter(
            known_outputs[:, 0],
            known_outputs[:, 1],
            c="blue",
            marker="^",
            label="Sampled designs",
        )
        ax.scatter(
            ypredict[:, 0],
            ypredict[:, 1],
            c="red",
            label="Predicted Pareto designs",
        )

        if reference_video_name and video_idx != reference_video_idx:
            _, _, _, _, ref_ypredict_idx, _ = self._get_design_space(
                reference_video_name, enable_tracking, enable_persist
            )

            filtered_idx = [idx for idx in ref_ypredict_idx if idx in known_idx]
            requested_idx = [
                int(idx) for idx in ref_ypredict_idx if idx not in known_idx
            ]

            if requested_idx:
                requested_idx_ref = storage_ref.child("requested_idx")
                requested_idx_all = requested_idx_ref.get() or []
                requested_idx_all.extend(requested_idx)
                requested_idx_ref.set(list(set(requested_idx_all)))

            ax.scatter(
                y[filtered_idx, 0],
                y[filtered_idx, 1],
                c="orange",
                label=f"Predicted Pareto designs for Video {reference_video_idx + 1}",
            )

        ax.set_title(
            f"Video {video_idx + 1}"
            # + f" with Tracking {'Enabled' if enable_tracking else 'Disabled'}"
            # + f" and Persistence {'Enabled' if enable_persist else 'Disabled'}"
            # + " Design Space"
        )
        ax.set(xlabel="Recall", ylabel="Precision")
        # ax.label_outer()
        # ax.legend()
        # plt.legend(bbox_to_anchor=(1.05, 1.05))
        # plt.xlabel("Recall")
        # plt.ylabel("Precision")
        ax.set_xlim(known_outputs[:, 0].min(), known_outputs[:, 0].max())
        ax.set_ylim(known_outputs[:, 1].min(), known_outputs[:, 1].max())

        # plt.show()

    def _get_row_col(self, i: int):
        col = i % 3
        row = math.floor(i / 3)

        return (row, col)

    def execute(self, args: Namespace):
        initialize_app()

        enable_tracking = True
        enable_persist = False

        video_files = [""]
        video_files.extend(Plot.VIDEO_FILES)

        with open("./output/pareto_front.csv", "w", encoding="utf8") as f:
            for ref_idx, ref_video_file in enumerate(video_files):
                ref_idx -= 1
                ref_video_name = None
                if ref_idx != -1:
                    ref_r, ref_c = self._get_row_col(ref_idx)

                    if ref_r == 0 and ref_c == 0:
                        ref_r = 1

                    dataset_path = get_dataset_path(ref_video_file)
                    ref_video_name = dataset_path.split("/")[-1]

                plt.clf()
                fig, axs = plt.subplots(nrows=3, ncols=3, figsize=(12, 8))
                fig.delaxes(axs[2][1])
                fig.delaxes(axs[2][2])
                for i, video_file in enumerate(Plot.VIDEO_FILES):
                    r, c = self._get_row_col(i)

                    self._get_results(
                        video_file, True, False, ref_video_name, axs[r, c]
                    )
                    # self._get_results(video_file, False, True)

                if ref_idx == -1:
                    ref_r = 0

                handles, labels = axs[ref_r, 0].get_legend_handles_labels()
                fig.tight_layout()
                fig.legend(
                    handles, labels, loc="lower right", bbox_to_anchor=(0.8, 0.15)
                )

                makedirs("./output/figures", exist_ok=True)

                if ref_idx == -1:
                    path = f"./output/figures/fig_{'tracking' if enable_tracking else 'detection'}_pareto.pdf"
                else:
                    path = f"./output/figures/fig_{'tracking' if enable_tracking else 'detection'}_pareto_ref{ref_idx + 1}.pdf"

                plt.savefig(path, format="pdf")

                if ref_idx != -1:
                    (
                        y,
                        known_outputs,
                        known_idx,
                        ypredict,
                        ypredict_idx,
                        storage_ref,
                    ) = self._get_design_space(
                        ref_video_name, enable_tracking, enable_persist
                    )

                    # print(f"Video {ref_idx + 1}")
                    for idx, (recall, precision, f1) in zip(known_idx, known_outputs):
                        f.write(
                            f"Video {ref_idx + 1},{idx},{recall},{precision},{f1}\n"
                        )
                        # print(f"{idx}: {recall},{precision},{f1}")

                # plt.show()
