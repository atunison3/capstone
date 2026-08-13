import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pandas import DataFrame
from typing import Any

from capstone.helper_functions import load_model_config, setup_logger
from capstone.data_cleaning import load_full_dataframe
from capstone.visualization.visuals import ColorScheme, OUTPUT_DIR, PLT_PARAMS, Y_LABEL

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
TWO_HUE = [ColorScheme.GREY, ColorScheme.UM_BLUE]

logger = setup_logger()

mpl.rcParams.update(PLT_PARAMS)  # type: ignore


def fig_bars_zoom(df: DataFrame) -> None:
    """Bar chart. The y-axis does not start at 0, so bar length is not proportional to
    turnout.
    """

    fig, ax = plt.subplots(figsize=(8.5, 5.2))

    # Plot the turnout for contacted and not contacted voters
    ax.plot([LABEL[c] for c in ORDER], df["Contacted"], marker="o", color=ColorScheme.UM_BLUE)
    ax.plot([LABEL[c] for c in ORDER], df["Not Contacted"], marker="o", color=ColorScheme.GREY)

    # Create the yellow fill between
    ax.fill_between(
        [LABEL[c] for c in ORDER], df["Contacted"], df["Not Contacted"], alpha=0.3, color=ColorScheme.UM_MAIZE
    )

    # Modify the axis
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.yaxis.grid(True, color=ColorScheme.LIGHT_GRAY, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylabel(Y_LABEL)
    ax.set_title("Outreach x Voter ID Strictness Interaction")

    # Save the layout
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "report_fig3_turnout_by_contacted.png")
    plt.close(fig)


def generate_fig3(config: dict[Any, Any]):

    # Make sure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load the dataframe and collect statistics
    frame = load_full_dataframe(config)

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

    # Perform groupby operations to get number of people voting and the count in each category
    frame["Count"] = [1] * len(frame)
    voted = frame.groupby(["NCSL Classification", "Contacted"])["Voted"].sum().reset_index()
    total = frame.groupby(["NCSL Classification", "Contacted"])["Count"].count().reset_index()
    merged = voted.merge(total, on=["NCSL Classification", "Contacted"])
    merged["Percent"] = merged["Voted"] / merged["Count"]
    pivot = merged.pivot(index="NCSL Classification", columns="Contacted", values="Percent").reset_index()
    pivot.columns.name = None
    pivot.index.name = None

    # Create the visual and save
    try:
        fig_bars_zoom(pivot)
        logger.info(f"🟢 Saved figure to {OUTPUT_DIR}")
    except Exception as e:
        logger.error(f"🔴 Failed to save figure to {OUTPUT_DIR}: {e}")


if __name__ == "__main__":
    # Load the config
    config = load_model_config()
