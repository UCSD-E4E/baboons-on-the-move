import pickle
from typing import Dict, List
import numpy as np
import pandas as pd
from library.design_space import DesignSpaceCache, get_design_space, get_pareto_front
import matplotlib.pyplot as plt
import math
from matplotlib.axes import Axes
from genericpath import exists

from library.firebase import initialize_app
from library.debug import trace


def get_video_files_dict(dataset_name: str) -> Dict[str, str]:
    if dataset_name.lower() == "viso":
        return {
            "Video 1": "VISO/car/003",
            "Video 2": "VISO/car/004",
            "Video 3": "VISO/car/005",
            "Video 4": "VISO/car/006",
            "Video 5": "VISO/car/007",
            "Video 6": "VISO/car/008",
            "Video 7": "VISO/car/009",
        }
    elif dataset_name.lower() == "baboons":
        return {"Video 1": "Baboons/NeilThomas/001"}

    raise Exception(f"{dataset_name} does not exist.")


def get_video_files(dataset_name: str) -> List[str]:
    if dataset_name.lower() == "viso":
        return [
            "VISO/car/003",
            "VISO/car/004",
            "VISO/car/005",
            "VISO/car/006",
            "VISO/car/007",
            "VISO/car/008",
            "VISO/car/009",
        ]
    elif dataset_name.lower() == "baboons":
        return ["Baboons/NeilThomas/001"]

    raise Exception(f"{dataset_name} does not exist.")


def _get_metric(table_v: pd.DataFrame, name: str) -> np.ndarray:
    array = np.zeros((table_v.shape[0], 7))
    array[:, 0] = table_v[("Video 1", name)]
    array[:, 1] = table_v[("Video 2", name)]
    array[:, 2] = table_v[("Video 3", name)]
    array[:, 3] = table_v[("Video 4", name)]
    array[:, 4] = table_v[("Video 5", name)]
    array[:, 5] = table_v[("Video 6", name)]
    array[:, 6] = table_v[("Video 7", name)]

    return array


def get_viso_table_v():
    return pd.read_csv("./plots/viso_table_v.csv", header=[0, 1], comment="#")


def get_viso_table_vi():
    return pd.read_csv("./plots/viso_table_vi.csv", comment="#")


def _get_video_results(
    dataset: str,
    enable_tracking=True,
    enable_persist=False,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    disable_network=False,
):
    _, y, _, _ = get_design_space(
        dataset,
        enable_tracking,
        enable_persist,
        max_width=max_width,
        max_height=max_height,
        allow_overlap=allow_overlap,
        disable_network=disable_network,
    )

    idx = np.argmax(y[:, 2])
    row = y[idx, :]

    return row


def get_dataset_results(
    dataset_name: str,
    enable_tracking=True,
    enable_persist=False,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    disable_network=False,
):
    df = pd.DataFrame(columns=["Video Name", "Recall", "Precision", "F1", "AP"])

    for name, dataset in get_video_files_dict(dataset_name).items():
        row = _get_video_results(
            dataset,
            enable_tracking=enable_tracking,
            enable_persist=enable_persist,
            max_width=max_width,
            max_height=max_height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )

        ypredict, _ = get_pareto_front(
            dataset,
            enable_tracking,
            enable_persist,
            max_width=max_width,
            max_height=max_height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )
        ypredict_order = np.argsort(ypredict[:, 0])
        ypredict = ypredict[ypredict_order, :]

        area = np.trapz(ypredict[:, 1], x=ypredict[:, 0])
        area += ypredict[0, 0] * ypredict[0, 1]

        df.loc[len(df.index)] = (
            [name]
            + list((np.round(row * 100) / 100).flatten())
            + [round(area * 100) / 100]
        )

    return df


def add_spot_row_viso_table_v(
    table_v: pd.DataFrame,
    enable_tracking=True,
    enable_persist=False,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    disable_network=False,
):
    spot = np.zeros((7, 3))

    for name, dataset in get_video_files_dict("VISO").items():
        video_idx = int(name[len("Video ") :]) - 1
        row = _get_video_results(
            dataset,
            enable_tracking=enable_tracking,
            enable_persist=enable_persist,
            max_width=max_width,
            max_height=max_height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )

        spot[video_idx, :] = row

    spot = ["Spot"] + list(np.round(spot.flatten(), decimals=2))
    df = table_v.copy()
    df.loc[len(df.index)] = spot

    return df


def add_spot_row_viso_table_vi(
    table_vi: pd.DataFrame,
    enable_tracking=True,
    enable_persist=False,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    disable_network=False,
):
    spot = np.zeros(7)

    for name, dataset in get_video_files_dict("VISO").items():
        video_idx = int(name[len("Video ") :]) - 1

        ypredict, _ = get_pareto_front(
            dataset,
            enable_tracking,
            enable_persist,
            max_width=max_width,
            max_height=max_height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )
        ypredict_order = np.argsort(ypredict[:, 0])
        ypredict = ypredict[ypredict_order, :]

        area = np.trapz(ypredict[:, 1], x=ypredict[:, 0])
        area += ypredict[0, 0] * ypredict[0, 1]

        spot[video_idx] = area

    spot = ["Spot"] + list(np.round(spot, decimals=2))
    df = table_vi.copy()
    df.loc[len(df.index)] = spot

    return df


def add_average_column_viso_table_v(table_v: pd.DataFrame):
    avg_recalls = np.average(_get_metric(table_v, "Recall"), axis=1)
    avg_precisions = np.average(_get_metric(table_v, "Precision"), axis=1)
    avg_f1s = np.average(_get_metric(table_v, "F1"), axis=1)
    avg = np.round(np.array([avg_recalls, avg_precisions, avg_f1s]).T, decimals=2)

    avg_df = pd.DataFrame(
        avg,
        columns=pd.MultiIndex.from_tuples(
            [("Average", "Recall"), ("Average", "Precision"), ("Average", "F1")]
        ),
    )

    df = table_v.join(avg_df)
    return df


def add_map_column_viso_table_vi(table_vi: pd.DataFrame):
    map_df = pd.DataFrame(
        np.round(np.average(table_vi.iloc[:, 1:].to_numpy(), axis=1), decimals=2),
        columns=["mAP"],
    )

    df = table_vi.join(map_df)
    return df


def _get_citations():
    return {
        "FD": "\\cite{cao_two_2015}",
        "ABM": "\\cite{gutchess_background_2001}",
        "MGBS": "\\cite{hutchison_detection_2010}",
        "GMM": "\\cite{zivkovic_efficient_2006}",
        "AGMM": "\\cite{horng-horng_lin_regularized_2011}",
        "VIBE": "\\cite{barnich_vibe_2011}",
        "FPCP": "\\cite{rodriguez_fast_2013}",
        "GoDec": "\\cite{zhou_godec_nodate}",
        "DECOLOR": "\\cite{xiaowei_zhou_moving_2013}",
        "FRMC": "\\cite{rezaei_background_2017}",
        "ClusterNet": "\\cite{lalonde_clusternet_2018}",
        "DTTP": "\\cite{ahmadi_moving_2019}",
        "D\&T": "\\cite{ao_needles_2020}",
        "MMB": "\\cite{yin_detecting_2022}",
    }


def df2latex_table_v(df: pd.DataFrame, table_index: int):
    cite = _get_citations()

    table = """
\\begin{tabular}{c c c c c c c c c c c c c c}
    \\hline\\\\
"""

    table += "    Method & "
    video_titles = list({v for v, _ in df.columns if v.strip()})
    video_titles.sort(key=lambda x: x[len("Video ") :] if "Video" in x else x)
    video_titles = video_titles[
        table_index * 3 + table_index : (table_index + 1) * 3 + 1 + table_index
    ]
    table += " & ".join("\\multicolumn{3}{c}{" + v + "}" for v in video_titles)
    table += "\\\\\n"

    table += """    & Recall & Precision & F1 & Recall & Precision & F1 & Recall & Precision & F1 & Recall & Precision & F1\\\\
    \\hline\\\\
"""

    for i in range(df.shape[0]):
        name = df.iloc[i, 0].replace("&", "\\&")

        table += "    "
        table += f"{name} {cite[name] if name in cite else ''}"

        for j in range(1 + table_index * 12, 13 + table_index * 12):
            max_column = df.iloc[:, j].max()

            is_max = max_column == df.iloc[i, j]
            is_second = (
                max([v for v in df.iloc[:, j] if v != max_column]) == df.iloc[i, j]
            )

            color = ""
            if is_max:
                color = "red"
            elif is_second:
                color = "blue"

            if color:
                color = "\\textcolor{" + color + "}{"

            table += " & " + color + f"{df.iloc[i, j]:.2f}"

            if color:
                table += "}"

        table += f"\\\\\n"

    table += """    \hline\\\\
\\end{tabular}"""

    return table


def df2latex_table_vi(df: pd.DataFrame):
    cite = _get_citations()

    table = """
\\begin{tabular}{c c c c c c c c c}
    \\hline \\\\
    Method & Video 1 & Video 2 & Video 3 & Video 4 & Video 5 & Video 6 & Video 7 & mAP\\\\
    \\hline \\\\
"""

    for i in range(df.shape[0]):
        name = df.iloc[i, 0].replace("&", "\\&")

        table += "    "
        table += f"{name} {cite[name] if name in cite else ''}"

        for j in range(1, 9):
            max_column = df.iloc[:, j].max()

            is_max = max_column == df.iloc[i, j]
            is_second = (
                max([v for v in df.iloc[:, j] if v != max_column]) == df.iloc[i, j]
            )

            color = ""
            if is_max:
                color = "red"
            elif is_second:
                color = "blue"

            if color:
                color = "\\textcolor{" + color + "}{"

            table += " & " + color + f"{df.iloc[i, j]:.2f}"

            if color:
                table += "}"

        table += f"\\\\\n"

    table += """    \hline\\\\
\\end{tabular}"""

    return table


def maximum_value_in_column(column):
    max_highlight = "background-color: red;"
    second_highlight = "background-color: blue;"
    third_highlight = "background-color: gray;"
    default = ""

    maximum_in_column = column.max()
    second_in_column = max([v for v in column if v != maximum_in_column])
    thrid_in_column = max(
        [v for v in column if v != maximum_in_column and v != second_in_column]
    )

    styles = []
    for v in column:
        if isinstance(v, str):
            styles.append(default)
            continue

        if v == maximum_in_column:
            styles.append(max_highlight)
            continue

        if v == second_in_column:
            styles.append(second_highlight)
            continue

        if v == thrid_in_column:
            styles.append(third_highlight)
            continue

        styles.append(default)

    return styles


def get_row_col(i: int):
    col = i % 3
    row = math.floor(i / 3)

    return (row, col)


def _plot_pareto_graph(
    dataset_name: str,
    video_name: str,
    video_file: str,
    ax: Axes,
    enable_tracking=True,
    enable_persist=False,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    ref_video_file=None,
    hide_title=False,
    disable_network=False,
):
    X, y, current_idx, known_idx = get_design_space(
        video_file,
        enable_tracking,
        enable_persist,
        max_width=max_width,
        max_height=max_height,
        allow_overlap=allow_overlap,
        disable_network=disable_network,
    )
    (ypredict, _,) = get_pareto_front(
        video_file,
        enable_tracking,
        enable_persist,
        max_width=max_width,
        max_height=max_height,
        allow_overlap=allow_overlap,
        disable_network=disable_network,
    )

    current_outputs = y[current_idx, :]

    ax.scatter(
        current_outputs[:, 0],
        current_outputs[:, 1],
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

    if ref_video_file is not None and video_file != ref_video_file:
        (_, ref_ypredict_idx,) = get_pareto_front(
            ref_video_file,
            enable_tracking,
            enable_persist,
            max_width=max_width,
            max_height=max_height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )

        ref_ypredict_idx_set = set(int(idx) for idx in ref_ypredict_idx)
        known_idx_set = set(int(idx) for idx in known_idx)

        missing_idx = ref_ypredict_idx_set.difference(known_idx_set)
        # if missing_idx:
        #     print(missing_idx)

        selected_idx = list(ref_ypredict_idx_set.intersection(known_idx_set))

        dataset_dict = get_video_files_dict(dataset_name)
        ref_video_name = [k for k, v in dataset_dict.items() if v == ref_video_file][0]
        ax.scatter(
            y[selected_idx, 0],
            y[selected_idx, 1],
            c="orange",
            marker="+",
            label=f"Predicted Pareto designs for {ref_video_name}",
        )

    if not hide_title:
        ax.set_title(video_name)
    ax.set(xlabel="Recall", ylabel="Precision")
    ax.set_xlim(current_outputs[:, 0].min(), current_outputs[:, 0].max())
    ax.set_ylim(current_outputs[:, 1].min(), current_outputs[:, 1].max())


def plot_pareto_front(
    dataset_name: str,
    max_cols=3,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    ref_video_file=None,
    disable_network=False,
):
    video_files = get_video_files(dataset_name)
    cols = min(max_cols, len(video_files))
    rows_total = float(len(video_files)) / float(cols)
    rows = math.ceil(rows_total)
    axs_to_delete = round((math.ceil(rows_total) - rows_total) * cols)

    fig, axs = plt.subplots(
        nrows=rows,
        ncols=cols,
        figsize=(4 * cols, 8 / 3 * rows),
        constrained_layout=True,
    )
    for i in range(axs_to_delete):
        fig.delaxes(axs[rows - 1][cols - 1 - i])

    dataset_dict = get_video_files_dict(dataset_name)
    for idx, video_file in enumerate(video_files):
        video_name = [k for k, v in dataset_dict.items() if v == video_file][0]
        r, c = get_row_col(idx)

        if len(video_files) > 1:
            ax = axs[r, c]
        else:
            ax = axs

        _plot_pareto_graph(
            dataset_name,
            video_name,
            video_file,
            ax,
            max_width=max_width,
            max_height=max_height,
            allow_overlap=allow_overlap,
            ref_video_file=ref_video_file,
            hide_title=len(video_files) <= 1,
            disable_network=disable_network,
        )

    title = f"{dataset_name} Pareto Front"
    idx = 0
    if ref_video_file is not None:
        ref_video_name = [k for k, v in dataset_dict.items() if v == ref_video_file][0]
        title = f"{title} with Pareto Front from {ref_video_name}"

        ref_idx = video_files.index(ref_video_file)
        if ref_idx == 0:
            idx = 1

    if len(video_files) > 1:
        ax = axs[idx, 0]
    else:
        ax = axs

    handles, labels = ax.get_legend_handles_labels()

    if len(video_files) > 1:
        fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.8, 0.15))
    else:
        fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.725, 0.4))

    fig.suptitle(title)

    return fig


def plot_pareto_front_ref(
    dataset_name: str,
    max_cols=3,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    ref_video_files=None,
    disable_network=False,
):
    video_files = get_video_files(dataset_name)

    if ref_video_files is None:
        ref_video_files = video_files

    figs = []

    for ref_video_file in ref_video_files:
        figs.append(
            (
                ref_video_file,
                plot_pareto_front(
                    dataset_name,
                    max_cols=max_cols,
                    max_width=max_width,
                    max_height=max_height,
                    allow_overlap=allow_overlap,
                    ref_video_file=ref_video_file,
                    disable_network=disable_network,
                ),
            )
        )

    return figs
