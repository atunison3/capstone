import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame

from capstone.helper_functions import load_model_config, get_data_path
from capstone.data_cleaning import load_full_dataframe
from capstone.visualization.visuals import Y_LABEL, OUTPUT_DIR, PLT_PARAMS, ColorScheme, compute_turnout_by_category

ORDER = ["Not Contacted", "Contacted"]
LABEL = {"Not Contacted": "Not Contacted", "Contacted": "Contacted"}
TWO_HUE = [ColorScheme.GREY, ColorScheme.UM_BLUE]

mpl.rcParams.update(PLT_PARAMS)  # type: ignore


def fig_bars_zoom(s: DataFrame) -> None:
    """Bar chart. The y-axis does not start at 0, so bar length is not proportional to
    turnout.
    """
    pcts = s["pct"].to_numpy(dtype=float)
    cis = s["ci"].to_numpy(dtype=float)

    # Zoom to the occupied range.
    ylo = float(np.floor(((pcts - cis).min() - 1.0) / 2) * 2)
    yhi = float(np.ceil(((pcts + cis).max() + 1.5) / 2) * 2)
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.bar(
        [LABEL[c] for c in ORDER],
        pcts,
        yerr=cis,
        color=TWO_HUE,
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
    ax.set_title("Turnout by contactedness, with 95% confidence intervals")

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
    fig.savefig(OUTPUT_DIR / "report_fig2_turnout_by_contacted.png")
    plt.close(fig)


if __name__ == "__main__":
    # Load the config
    model_config = load_model_config()

    # Create data path
    data_path = get_data_path() / "prod"

    # Make sure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load the dataframe and collect statistics
    frame = load_full_dataframe(data_path, model_config)

    # Determine who was contacted
    frame["Contacted"] = (
        frame[
            [
                "In person",
                "Phone call",
                "Email or text message",
                "Letter or postcard",
            ]
        ]
        .eq("Yes")  # type: ignore
        .any(axis=1)
        .map({True: "Contacted", False: "Not Contacted"})
    )
    stats = compute_turnout_by_category(frame, "Contacted", ORDER)

    try:
        fig_bars_zoom(stats)
        print(f"\nSaved figure to {OUTPUT_DIR}")
    except Exception as e:
        print(f"Failed to save figure to {OUTPUT_DIR}: {e}")
