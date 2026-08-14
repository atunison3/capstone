from enum import StrEnum
from numpy import sqrt
from pandas import DataFrame
from pathlib import Path


class ColorScheme(StrEnum):
    UM_BLUE = "#00274C"  # NAVY
    UM_MAIZE = "#FFCB05"  # MAIZE
    ARB_BLUE = "#2F65A7"  #
    RACK_GRN = "#75988D"  #
    UMMA_TAN = "#CFC096"  #
    TAPPAN_RD = "#9A3324"  #
    ASH = "#989C97"  #
    UM_BLUE2 = "#2E4E6E"  # NAVY2
    UM_BLUE3 = "#7C97B3"  # NAVY3
    GREY = "#B7B7B7"
    INK = "#00274C"
    LIGHT_GRAY = "#E5E5E5"


# Anchor to repo root so scripts work regardless of cwd.
# visuals.py lives at <repo>/capstone/visualization/visuals.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "docs" / "assets"

PLT_PARAMS: dict[str, object] = {
    "figure.dpi": 140,
    "savefig.dpi": 140,
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlecolor": ColorScheme.UM_BLUE,
    "axes.labelcolor": ColorScheme.UM_BLUE,
    "text.color": ColorScheme.UM_BLUE,
    "xtick.color": ColorScheme.UM_BLUE,
    "ytick.color": ColorScheme.UM_BLUE,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
}

Y_LABEL = "Validated turnout (%)"


def ensure_output_dir(path: Path = OUTPUT_DIR) -> Path:
    """Create the figure output directory if needed."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def compute_turnout_by_category(df: DataFrame, category: str, order: list[str]) -> DataFrame:
    """Turnout rate and 95% CI per contact level"""

    g = df.groupby(category, observed=True)["Voted"]

    out = DataFrame({"n": g.count(), "pct": g.mean() * 100}).reindex(order)

    p = out["pct"] / 100
    out["ci"] = 1.96 * sqrt(p * (1 - p) / out["n"]) * 100

    return out
