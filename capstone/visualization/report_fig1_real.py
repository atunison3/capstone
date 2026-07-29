"""
Script to generate figure that describes turnout by voter-ID law strictness, on the 2024 CES data.

Output:
  figures/report_fig1_turnout_by_strictness.png
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from capstone.data_cleaning import (
    load_dataframe,
    load_fips_data,
    load_voter_id_effect,
    merge_fips_ncsl,
)
from capstone.helper_functions import load_config

# UM palette
UM_BLUE, UM_MAIZE = "#00274C", "#FFCB05"
ARB_BLUE, RACK_GRN, UMMA_TAN, TAPPAN_RD, ASH = "#2F65A7", "#75988D", "#CFC096", "#9A3324", "#989C97"

# Bar colors
FIVE_HUE = [UM_BLUE, ARB_BLUE, RACK_GRN, UMMA_TAN, UM_MAIZE]

mpl.rcParams.update(
    {
        "figure.dpi": 140, "savefig.dpi": 140, "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlecolor": UM_BLUE,
        "axes.labelcolor": UM_BLUE, "text.color": UM_BLUE,
        "xtick.color": UM_BLUE, "ytick.color": UM_BLUE,
        "figure.facecolor": "white", "axes.facecolor": "white",
    }
)

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

ORDER = [
    "No Document Required to Vote",
    "Non-Strict, Non-Photo ID",
    "Non-Strict Photo ID",
    "Strict Non-Photo ID",
    "Strict Photo ID",
]
LABEL = {
    "No Document Required to Vote": "No ID\nrequired",
    "Non-Strict, Non-Photo ID": "Non-strict\nnon-photo",
    "Non-Strict Photo ID": "Non-strict\nphoto",
    "Strict Non-Photo ID": "Strict\nnon-photo",
    "Strict Photo ID": "Strict\nphoto",
}
def build_frame() -> pd.DataFrame:
    """Join CES respondents to their state's NCSL strictness classification."""
    data_path = Path(load_config()["data_path"]) / "dev"
    df = load_dataframe(data_path)
    states = merge_fips_ncsl(load_fips_data(data_path), load_voter_id_effect(data_path))

    combined = df.merge(states, left_on="inputstate", right_on="State FIPS Code", how="left")

    dropped = int(combined["NCSL Classification"].isna().sum())
    if dropped:
        print(f"note: dropping {dropped} respondents with no classification (DC)")
    combined = combined[combined["NCSL Classification"].notna()].copy()

    # count not matched as didn't vote
    combined["turnout"] = combined["TS_g2024"].isin([1, 2, 3, 4, 5, 6]).astype(int)
    combined["strictness"] = pd.Categorical(
        combined["NCSL Classification"], categories=ORDER, ordered=True
    )
    return combined


def compute_turnout_by_strictness(df: pd.DataFrame) -> pd.DataFrame:
    """Turnout rate and 95% CI per strictness level."""
    g = df.groupby("strictness", observed=True)["turnout"]
    out = pd.DataFrame({"n": g.count(), "pct": g.mean() * 100}).reindex(ORDER)
    p = out["pct"] / 100
    out["ci"] = 1.96 * np.sqrt(p * (1 - p) / out["n"]) * 100
    return out


def fig_bars_zoom(s: pd.DataFrame) -> None:
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
        [LABEL[c] for c in ORDER], pcts, yerr=cis,
        color=FIVE_HUE, capsize=6, edgecolor="white", linewidth=0.8, width=0.62,
        error_kw=dict(ecolor=TAPPAN_RD, elinewidth=2.2, capthick=2.2, zorder=5),
    )
    for i, (pct, ci) in enumerate(zip(pcts, cis)):
        ax.text(i, pct + ci + 0.35, f"{pct:.1f}%",
                ha="center", fontsize=10.5, color=UM_BLUE, fontweight="bold")
    ax.set_ylim(ylo, yhi)
    ax.set_yticks(np.arange(ylo, yhi + 1, 2))
    ax.yaxis.grid(True, color="#E5E5E5", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylabel("Validated turnout (%)")
    ax.set_title("Turnout by voter-ID strictness, with 95% confidence intervals")

    ax.plot([0], [0], transform=ax.transAxes, clip_on=False, color=UM_BLUE,
            marker=[(-1, -0.6), (1, 0.6)], markersize=9, markeredgewidth=1.4, linestyle="none")

    fig.tight_layout()
    fig.savefig(OUT / "report_fig1_turnout_by_strictness.png")
    plt.close(fig)


if __name__ == "__main__":
    frame = build_frame()
    stats = compute_turnout_by_strictness(frame)

    print(f"\nN = {len(frame):,}   overall turnout = {frame['turnout'].mean() * 100:.1f}%\n")
    print(stats.round(2).to_string())

    fig_bars_zoom(stats)
    print(f"\nSaved figure to {OUT}")
