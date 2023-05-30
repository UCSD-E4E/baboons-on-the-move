"""
Helpers for plotting results for Spot paper.
"""

import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from library.design_space import get_design_space, get_pareto_front


def get_video_files_dict(dataset_name: str) -> Dict[str, str]:
    """
    Gets the video files for the specified dataset.
    """
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
        return {
            "Video 1": "Baboons/NeilThomas/001",
            "Video 2": "Baboons/NeilThomas/002",
        }

    raise Exception(f"{dataset_name} does not exist.")


def get_video_files(dataset_name: str) -> List[str]:
    """
    Gets a list of video files for the specified dataset.
    """
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
        return ["Baboons/NeilThomas/001", "Baboons/NeilThomas/002"]

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
    """
    Gets the precision, recall, F1 table from Yin et al.
    """
    return pd.read_csv("./plots/viso_table_v.csv", header=[0, 1], comment="#")


def get_viso_table_vi():
    """
    Gets the AP, mAP table from Yin et al.
    """
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
    max_width: int or Tuple[int, int] = None,
    max_height: int or Tuple[int, int] = None,
    allow_overlap=False,
    disable_network=False,
    video_file_override: List[str] = None,
):
    """
    Gets the dataset results for the specified dataset.
    """

    df = pd.DataFrame(
        columns=[
            "Video Name",
            "Recall",
            "Precision",
            "F1",
            "AP",
        ]
    )

    count = len(get_video_files_dict(dataset_name).items())
    if type(max_width) is not tuple:
        max_width = (max_width,) * count

    if type(max_height) is not tuple:
        max_height = (max_height,) * count

    for width, height, (name, dataset) in zip(
        max_width, max_height, get_video_files_dict(dataset_name).items()
    ):
        if video_file_override and name not in video_file_override:
            continue

        row = _get_video_results(
            dataset,
            enable_tracking=enable_tracking,
            enable_persist=enable_persist,
            max_width=width,
            max_height=height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )

        ypredict, _ = get_pareto_front(
            dataset,
            enable_tracking,
            enable_persist,
            max_width=width,
            max_height=height,
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


def get_sherlock_table(
    enable_tracking=True, enable_persist=False, disable_network=False
):
    """
    Gets the table of each of the Sherlock objective functions.
    """

    df_video1_35_no = get_dataset_results(
        "VISO",
        enable_tracking=enable_tracking,
        enable_persist=enable_persist,
        max_width=35,
        max_height=35,
        allow_overlap=False,
        disable_network=disable_network,
        video_file_override=["Video 1"],
    )
    df_video1_35_yes = get_dataset_results(
        "VISO",
        enable_tracking=enable_tracking,
        enable_persist=enable_persist,
        max_width=35,
        max_height=35,
        allow_overlap=True,
        disable_network=disable_network,
        video_file_override=["Video 1"],
    )
    df_video1_1024_yes = get_dataset_results(
        "VISO",
        enable_tracking=enable_tracking,
        enable_persist=enable_persist,
        max_width=1024,
        max_height=1024,
        allow_overlap=True,
        disable_network=disable_network,
        video_file_override=["Video 1"],
    )

    df = pd.DataFrame([], columns=df_video1_35_no.columns)
    df.loc[len(df.index)] = df_video1_1024_yes.loc[0]
    df.loc[len(df.index)] = df_video1_35_yes.loc[0]
    df.loc[len(df.index)] = df_video1_35_no.loc[0]

    df.insert(
        1,
        "Objective Function",
        [
            "Problem Objective function 1",
            "Problem Objective function 2",
            "Final Objective Function",
        ],
        True,
    )
    df.insert(2, "Max Width", [1024, 35, 35], True)
    df.insert(3, "Max Height", [1024, 35, 35], True)
    df.insert(4, "Allow Overlap", ["yes", "yes", "no"], True)

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
    """
    Adds the Spot row to the precision, recall, f1 table.
    """

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
    """
    Adds the Spot row to the AP, mAP table.
    """

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
    """
    Adds the average column to the precision, recall, f1 table.
    """

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
    """
    Adds the mAP column to the VI table.
    """

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
        "D\\&T": "\\cite{ao_needles_2020}",
        "MMB": "\\cite{yin_detecting_2022}",
    }


def df2latex_table_v(df: pd.DataFrame, table_index: int):
    """
    Converts the table V dataframe to a latex table.
    """
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
                max(v for v in df.iloc[:, j] if v != max_column) == df.iloc[i, j]
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

        table += "\\\\\n"

    table += """    \\hline\\\\
\\end{tabular}"""

    return table


def df2latex_table_vi(df: pd.DataFrame):
    """
    Converts the table VI dataframe to latex.
    """
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
                max(v for v in df.iloc[:, j] if v != max_column) == df.iloc[i, j]
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

        table += "\\\\\n"

    table += """    \\hline\\\\
\\end{tabular}"""

    return table


def maximum_value_in_column(column):
    """
    Highlights the maximum and second largest value in each column in the dataframe.
    """

    max_highlight = "background-color: red;"
    second_highlight = "background-color: blue;"
    third_highlight = "background-color: gray;"
    default = ""

    maximum_in_column = column.max()
    second_in_column = max(v for v in column if v != maximum_in_column)
    thrid_in_column = max(
        v for v in column if v not in (maximum_in_column, second_in_column)
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


def _get_row_col(i: int):
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
    _, y, current_idx, known_idx = get_design_space(
        video_file,
        enable_tracking,
        enable_persist,
        max_width=max_width,
        max_height=max_height,
        allow_overlap=allow_overlap,
        disable_network=disable_network,
    )
    (
        ypredict,
        _,
    ) = get_pareto_front(
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
        label="Samples",
    )
    ax.scatter(
        ypredict[:, 0],
        ypredict[:, 1],
        c="red",
        label="Pareto Optimal Samples",
    )

    if ref_video_file is not None and video_file != ref_video_file:
        (
            _,
            ref_ypredict_idx,
        ) = get_pareto_front(
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

        # missing_idx = ref_ypredict_idx_set.difference(known_idx_set)
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
    """
    Plots the Pareto front for the specified dataset.
    """

    video_files = get_video_files(dataset_name)
    cols = min(max_cols, len(video_files))
    rows_total = float(len(video_files)) / float(cols)
    rows = math.ceil(rows_total)
    axs_to_delete = round((math.ceil(rows_total) - rows_total) * cols)

    count = len(get_video_files_dict(dataset_name).items())
    if type(max_width) is not tuple:
        max_width = (max_width,) * count

    if type(max_height) is not tuple:
        max_height = (max_height,) * count

    fig, axs = plt.subplots(
        nrows=rows,
        ncols=cols,
        figsize=(4 * cols, 8 / 3 * rows),
        constrained_layout=True,
    )
    for i in range(axs_to_delete):
        fig.delaxes(axs[rows - 1][cols - 1 - i])

    dataset_dict = get_video_files_dict(dataset_name)
    for width, height, (idx, video_file) in zip(
        max_width, max_height, enumerate(video_files)
    ):
        video_name = [k for k, v in dataset_dict.items() if v == video_file][0]
        r, c = _get_row_col(idx)

        if len(video_files) > 1:
            if rows > 1:
                ax = axs[r, c]
            else:
                ax = axs[c]
        else:
            ax = axs

        _plot_pareto_graph(
            dataset_name,
            video_name,
            video_file,
            ax,
            max_width=width,
            max_height=height,
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
        if rows > 1:
            ax = axs[idx, 0]
        else:
            ax = axs[idx]
    else:
        ax = axs

    handles, labels = ax.get_legend_handles_labels()

    if len(video_files) > 1:
        fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.8, 0.15))
    else:
        fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.725, 0.4))

    fig.suptitle(title)

    return fig


def plot_precision_recall_curve(
    dataset_name: str,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    display_pareto_front=False,
    fill=False,
    disable_network=False,
):
    """
    Plots the PR curve for the given dataset.
    """

    video_files = get_video_files(dataset_name)
    video_file = video_files[0]
    enable_tracking = True
    enable_persist = False
    cols = 1
    rows = 1

    fig, ax = plt.subplots(
        nrows=rows,
        ncols=cols,
        figsize=(4 * cols, 8 / 3 * rows),
        constrained_layout=True,
    )

    dataset_dict = get_video_files_dict(dataset_name)
    video_name = [k for k, v in dataset_dict.items() if v == video_file][0]

    _, y, current_idx, _ = get_design_space(
        video_file,
        enable_tracking,
        enable_persist,
        max_width=max_width,
        max_height=max_height,
        allow_overlap=allow_overlap,
        disable_network=disable_network,
    )
    (
        ypredict,
        _,
    ) = get_pareto_front(
        video_file,
        enable_tracking,
        enable_persist,
        max_width=max_width,
        max_height=max_height,
        allow_overlap=allow_overlap,
        disable_network=disable_network,
    )

    current_outputs = y[current_idx, :]
    ypredict_order = np.argsort(ypredict[:, 0])

    if display_pareto_front:
        ax.scatter(
            current_outputs[:, 0],
            current_outputs[:, 1],
            color=(0, 0, 1, 0.05),
            marker="^",
            label="Samples",
        )
        ax.scatter(
            ypredict[:, 0],
            ypredict[:, 1],
            color=(1, 0, 0, 0.1),
            label="Pareto Optimal Samples",
        )

    ypredict_extend = np.zeros((ypredict.shape[0] + 1, ypredict.shape[1]))
    ypredict_extend[1:, :] = ypredict[ypredict_order, :]
    ypredict_extend[0, 1] = ypredict[ypredict_order[0], 1]

    ax.plot(
        ypredict_extend[:, 0],
        ypredict_extend[:, 1],
        c="red",
        label="PR Curve",
    )

    if fill:
        ax.fill_between(
            ypredict_extend[:, 0],
            ypredict_extend[:, 1],
            where=ypredict_extend[:, 1] >= np.zeros(ypredict_extend.shape[0]),
            interpolate=True,
            color=(1, 0, 0, 0.45),
        )

    ax.set_title(video_name)
    ax.set(xlabel="Recall", ylabel="Precision")
    ax.set_xlim(current_outputs[:, 0].min(), current_outputs[:, 0].max())
    ax.set_ylim(current_outputs[:, 1].min(), current_outputs[:, 1].max())

    title = f"{dataset_name} "
    if display_pareto_front:
        title += "Pareto Front"
    elif fill:
        title += "Average Precision (AP)"
    else:
        title += "Precision-Recall (PR) Curve"

    handles, labels = ax.get_legend_handles_labels()

    if display_pareto_front:
        fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.71, 0.46))
    else:
        fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.45, 0.32))

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
    """
    Plots the Pareto front with reference to another Pareto front.
    """

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


def plot_sherlock_pareto_front(disable_network=False):
    """
    Plots the Pareto front for the VISO dataset, video 1 for each of Sherlock's objective functions.
    """

    settings = [(1024, 1024, True), (35, 35, True), (35, 35, False)]

    cols = 3
    rows = 1

    fig, axs = plt.subplots(
        nrows=rows,
        ncols=cols,
        figsize=(4 * cols, 8 / 3 * rows),
        constrained_layout=True,
    )

    for idx, (max_width, max_height, allow_overlap) in enumerate(settings):
        if idx != 2:
            video_name = f"Problem Objective function {idx + 1}"
        else:
            video_name = "Final Objective Function"

        ax = axs[idx]

        _plot_pareto_graph(
            None,
            video_name,
            "VISO/car/003",
            ax,
            max_width=max_width,
            max_height=max_height,
            allow_overlap=allow_overlap,
            hide_title=False,
            disable_network=disable_network,
        )

    title = "Comparison of Sherlock Objective Functions"
    idx = 0
    ax = axs[idx]

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(1, 0.6))
    fig.suptitle(title)

    return fig


def _add_pareto_front_to_dataframe(
    dataset: str,
    video_name: str,
    objective_function: str,
    y: np.ndarray,
    current_idx: np.ndarray,
    df: pd.DataFrame,
):
    current_outputs = np.array(y[current_idx, :])

    update = pd.DataFrame([], columns=df.columns)
    update["Dataset"] = [dataset] * current_outputs.shape[0]
    update["Video Name"] = [video_name] * current_outputs.shape[0]
    update["Objective Function"] = [objective_function] * current_outputs.shape[0]
    update["Index"] = current_idx
    update["Recall"] = current_outputs[:, 0]
    update["Precision"] = current_outputs[:, 1]
    update["F1"] = current_outputs[:, 2]

    return pd.concat([df, update])


def get_all_data(enable_tracking=True, enable_persist=False, disable_network=False):
    """
    Gets a list of all of the Spot data for each objective function to output to a CSV.
    """

    df = pd.DataFrame(
        [],
        columns=[
            "Dataset",
            "Video Name",
            "Objective Function",
            "Index",
            "Recall",
            "Precision",
            "F1",
        ],
    )

    _, y, current_idx, _ = get_design_space(
        "VISO/car/003",
        enable_tracking=enable_tracking,
        enable_persist=enable_persist,
        max_width=1024,
        max_height=1024,
        allow_overlap=True,
        disable_network=disable_network,
    )

    df = _add_pareto_front_to_dataframe(
        "VISO", "VISO/car/003", "Problem Objective function 1", y, current_idx, df
    )

    _, y, current_idx, _ = get_design_space(
        "VISO/car/003",
        enable_tracking=enable_tracking,
        enable_persist=enable_persist,
        max_width=35,
        max_height=35,
        allow_overlap=True,
        disable_network=disable_network,
    )

    df = _add_pareto_front_to_dataframe(
        "VISO", "VISO/car/003", "Problem Objective function 2", y, current_idx, df
    )

    for video_file in get_video_files("VISO"):
        _, y, current_idx, _ = get_design_space(
            video_file,
            enable_tracking=enable_tracking,
            enable_persist=enable_persist,
            max_width=35,
            max_height=35,
            allow_overlap=False,
            disable_network=disable_network,
        )

        df = _add_pareto_front_to_dataframe(
            "VISO", video_file, "Final Objective function", y, current_idx, df
        )

    return df


def get_sample_count(
    dataset_name,
    max_width=None,
    max_height=None,
    allow_overlap=False,
    disable_network=False,
):
    """
    Produces a dataframe that represents the list of samples per video.
    """

    video_files = get_video_files_dict(dataset_name)
    data = []

    count = len(video_files.items())
    if type(max_width) is not tuple:
        max_width = (max_width,) * count

    if type(max_height) is not tuple:
        max_height = (max_height,) * count

    for width, height, (video_name, dataset) in zip(
        max_width, max_height, video_files.items()
    ):
        _, y, _, known_idx = get_design_space(
            dataset,
            True,
            False,
            max_width=width,
            max_height=height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )

        ypredict, _ = get_pareto_front(
            dataset,
            True,
            False,
            max_width=width,
            max_height=height,
            allow_overlap=allow_overlap,
            disable_network=disable_network,
        )

        data.append(
            [
                video_name,
                len(known_idx),
                f"{round(len(known_idx) / float(y.shape[0]) * 10000) / 100}%",
                ypredict.shape[0],
            ]
        )

    df = pd.DataFrame(
        data,
        columns=[
            "Video Name",
            "Sampled Count",
            "Sampled Percent",
            "Pareto Optimal Count",
        ],
    )

    return df
