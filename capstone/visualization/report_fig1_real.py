"""
Script to generate figure that describes turnout by voter-ID law strictness, on the 2024 CES data.

Output:
  figures/report_fig1_turnout_by_strictness.png
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from pathlib import Path

from capstone.helper_functions import load_local_config, load_model_config
from capstone.data_cleaning import load_full_dataframe
from capstone.visualization.visuals import Y_LABEL, OUTPUT_DIR, PLT_PARAMS, ColorScheme, compute_turnout_by_category

# Bar colors
FIVE_HUE = [ColorScheme.UM_BLUE, ColorScheme.ARB_BLUE, ColorScheme.RACK_GRN, ColorScheme.UMMA_TAN, ColorScheme.UM_MAIZE]

ORDER = [
    "No Document Required to Vote",
    "Non-Strict, Non-Photo ID",
    "Non-Strict, Photo ID",
    "Strict, Non-Photo ID",
    "Strict, Photo ID",
]
LABEL = {
    "No Document Required to Vote": "No ID\nrequired",
    "Non-Strict, Non-Photo ID": "Non-strict\nnon-photo",
    "Non-Strict, Photo ID": "Non-strict\nphoto",
    "Strict, Non-Photo ID": "Strict\nnon-photo",
    "Strict, Photo ID": "Strict\nphoto",
}

mpl.rcParams.update(PLT_PARAMS)  # type: ignore


def fig_bars_zoom(s: DataFrame) -> None:
    """Bar chart. The y-axis does not start at 0, so bar length is not proportional to
    turnout.
    """
    pcts = s["pct"].to_numpy(dtype=float)
    cis = s["ci"].to_numpy(dtype=float)

    # Zoom to the occupied range.
    ylo = float(np.floor(((s["pct"] - s["ci"]).min() - 1.0) / 2) * 2)
    yhi = float(np.ceil(((s["pct"] + s["ci"]).max() + 1.5) / 2) * 2)
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.bar(
        [LABEL[c] for c in ORDER],
        pcts,
        yerr=cis,
        color=FIVE_HUE,
        capsize=6,
        edgecolor="white",
        linewidth=0.8,
        width=0.62,
        error_kw=dict(ecolor=ColorScheme.TAPPAN_RD, elinewidth=2.2, capthick=2.2, zorder=5),
    )
    for i, (pct, ci) in enumerate(zip(pcts, cis)):
        ax.text(
            i, pct + ci + 0.35, f"{pct:.1f}%", ha="center", fontsize=10.5, color=ColorScheme.UM_BLUE, fontweight="bold"
        )
    ax.set_ylim(ylo, yhi)
    ax.set_yticks(np.arange(ylo, yhi + 1, 2))
    ax.yaxis.grid(True, color=ColorScheme.LIGHT_GRAY, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylabel(Y_LABEL)
    ax.set_title("Turnout by voter-ID strictness, with 95% confidence intervals")

    ax.plot(
        [0],
        [0],
        transform=ax.transAxes,
        clip_on=False,
        color=ColorScheme.UM_BLUE,
        marker=[(-1, -0.6), (1, 0.6)],
        markersize=9,
        markeredgewidth=1.4,
        linestyle="none",
    )

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "report_fig1_turnout_by_strictness.png")
    plt.close(fig)


if __name__ == "__main__":

    # Load the config
    model_config = load_model_config()
    local_config = load_local_config()

    # Create data path
    data_path = Path(local_config["data_path"]) / "prod"

    # Make sure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load the dataframe and collect statistics
    frame = load_full_dataframe(data_path, model_config)
    stats = compute_turnout_by_category(frame, "NCSL Classification", ORDER)

    print(f"\nN = {len(frame):,}   overall turnout = {frame['Voted'].mean() * 100:.1f}%\n")
    print(stats.round(2).to_string())

    try:
        fig_bars_zoom(stats)
        print(f"\nSaved figure to {OUTPUT_DIR}")
    except Exception as e:
        print(f"Failed to save figure to {OUTPUT_DIR}: {e}")
