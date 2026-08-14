"""
Generate Figure 4: marginal effects from the logistic regression model.

The voter-ID effects compare each voter-ID classification against
"No Document Required to Vote", averaging predicted probabilities over
the observed sample.

The campaign-contact effect compares the observed outreach pattern among
contacted respondents against a counterfactual where those respondents
received no campaign outreach.

Output:
    figures/report_fig4_logistic_marginal_effects.png
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from patsy import build_design_matrices  # type: ignore
from scipy.special import expit  # type: ignore
from typing import Any, cast

from capstone.data_cleaning import load_full_dataframe
from capstone.helper_functions import load_model_config, setup_logger
from capstone.logistic_regression import train_model
from capstone.visualization.visuals import OUTPUT_DIR, PLT_PARAMS, ColorScheme, ensure_output_dir

REFERENCE_ID_LAW = "No Document Required to Vote"

ID_LAW_ORDER = [
    "Non-Strict, Non-Photo ID",
    "Non-Strict, Photo ID",
    "Strict, Non-Photo ID",
    "Strict, Photo ID",
]

ID_LAW_LABEL = {
    "Non-Strict, Non-Photo ID": "Strictness: non-strict, non-photo",
    "Non-Strict, Photo ID": "Strictness: non-strict, photo",
    "Strict, Non-Photo ID": "Strictness: strict, non-photo",
    "Strict, Photo ID": "Strictness: strict, photo",
}

CONTACT_COLUMNS = [
    "In person",
    "Phone call",
    "Email or text message",
    "Letter or postcard",
]

FORMULA = """
    Voted
    ~ C(Education)
    + C(Race)
    + C(Gender)
    + Age
    + Q("In person") * C(Q("NCSL Classification"))
    + Q("Phone call") * C(Q("NCSL Classification"))
    + Q("Email or text message") * C(Q("NCSL Classification"))
    + Q("Letter or postcard") * C(Q("NCSL Classification"))
"""

logger = setup_logger()

mpl.rcParams.update(PLT_PARAMS)  # type: ignore


def _design_matrix(model: Any, frame: DataFrame) -> np.ndarray:
    """Build the Patsy design matrix for new counterfactual data."""

    design_info = model.model.data.design_info

    matrix = build_design_matrices(
        [design_info],
        frame,
        return_type="dataframe",
    )[0]

    return matrix.to_numpy(dtype=float)


def _probability_contrast(
    model: Any,
    comparison: DataFrame,
    reference: DataFrame,
) -> tuple[float, float, float]:
    """
    Calculate an average probability contrast and a 95% confidence interval.

    The confidence interval uses the delta method and the covariance matrix
    from the fitted logistic regression.

    Returns values in percentage points.
    """

    # TODO: Verify this function. It is AI generated!!!!!!

    params = model.params.to_numpy(dtype=float)
    covariance = model.cov_params().to_numpy(dtype=float)

    x_comparison = _design_matrix(model, comparison)
    x_reference = _design_matrix(model, reference)

    p_comparison = expit(x_comparison @ params)
    p_reference = expit(x_reference @ params)

    differences = p_comparison - p_reference
    estimate = float(differences.mean())

    comparison_derivative = p_comparison * (1.0 - p_comparison)
    reference_derivative = p_reference * (1.0 - p_reference)

    gradient = (
        comparison_derivative[:, np.newaxis] * x_comparison - reference_derivative[:, np.newaxis] * x_reference
    ).mean(axis=0)

    variance = float(gradient @ covariance @ gradient)
    standard_error = float(np.sqrt(max(variance, 0.0)))

    lower = estimate - 1.96 * standard_error
    upper = estimate + 1.96 * standard_error

    return estimate * 100.0, lower * 100.0, upper * 100.0


def compute_marginal_effects(model: Any, frame: DataFrame) -> DataFrame:
    """Compute the average probability effects."""

    # Statsmodels may have dropped rows containing missing values.
    model_frame = frame.loc[model.model.data.row_labels].copy()

    rows: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Voter-ID law effects
    #
    # Compare everyone under each voter-ID classification against the
    # counterfactual where everyone lives under the reference classification.
    # ------------------------------------------------------------------

    for classification in ID_LAW_ORDER:
        comparison = model_frame.copy()
        reference = model_frame.copy()

        comparison["NCSL Classification"] = classification
        reference["NCSL Classification"] = REFERENCE_ID_LAW

        effect, lower, upper = _probability_contrast(
            model=model,
            comparison=comparison,
            reference=reference,
        )

        rows.append(
            {
                "label": ID_LAW_LABEL[classification],
                "effect": effect,
                "lower": lower,
                "upper": upper,
                "type": "strictness",
            }
        )

    # ------------------------------------------------------------------
    # Campaign-contact effect
    #
    # Restrict to people who actually received at least one type of outreach.
    # Compare their observed outreach pattern against receiving no outreach.
    # ------------------------------------------------------------------

    contacted_mask = model_frame[CONTACT_COLUMNS].eq("Yes").any(axis=1)

    contacted = model_frame.loc[contacted_mask].copy()
    no_contact = contacted.copy()

    no_contact[CONTACT_COLUMNS] = "No"

    effect, lower, upper = _probability_contrast(
        model=model,
        comparison=contacted,
        reference=no_contact,
    )

    rows.append(
        {
            "label": "Contacted by campaign",
            "effect": effect,
            "lower": lower,
            "upper": upper,
            "type": "contact",
        }
    )

    return DataFrame(rows)


def fig_marginal_effects(effects: DataFrame) -> None:
    """Plot average probability effects with 95% confidence intervals."""

    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    y_positions = np.arange(len(effects) - 1, -1, -1)

    for y_position, row in zip(y_positions, effects.itertuples()):

        # Force float types
        effect = float(cast(Any, row.effect))
        lower = float(cast(Any, row.lower))
        upper = float(cast(Any, row.upper))

        # Determine point color based on effect
        point_color = ColorScheme.TAPPAN_RD if effect < 0 else ColorScheme.UM_BLUE

        lower_error = effect - lower
        upper_error = upper - effect

        ax.errorbar(
            effect,
            y_position,
            xerr=np.array([[lower_error], [upper_error]]),
            fmt="o",
            markersize=8,
            color=point_color,
            ecolor=ColorScheme.GREY,
            elinewidth=1.8,
            capsize=5,
            capthick=1.8,
            zorder=3,
        )

    # Zero means no estimated change in turnout probability.
    ax.axvline(
        0,
        color=ColorScheme.GREY,
        linestyle="--",
        linewidth=1.2,
        alpha=0.8,
        zorder=1,
    )

    # Dynamically choose x-axis limits from the confidence intervals.
    minimum = float(effects["lower"].min())
    maximum = float(effects["upper"].max())

    x_lower = np.floor((minimum - 0.5) / 2.0) * 2.0
    x_upper = np.ceil((maximum + 0.5) / 2.0) * 2.0

    ax.set_xlim(x_lower, x_upper)
    ax.set_xticks(np.arange(x_lower, x_upper + 0.1, 2.0))

    ax.set_yticks(y_positions)
    ax.set_yticklabels(effects["label"])

    ax.set_xlabel("Change in Prob(voted), percentage points (95% CI)")
    ax.set_title(
        "Estimated effects on turnout, holding demographics constant",
        fontweight="bold",
    )

    ax.grid(False)

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "report_fig4_logistic_marginal_effects.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def generate_fig4(config: dict[Any, Any]) -> None:
    """Fit the logistic regression and create Figure 4."""

    ensure_output_dir()

    df = load_full_dataframe(config)

    try:
        model = train_model(df)

        logger.info("🟢 Logistic regression fitted successfully.")

        effects = compute_marginal_effects(model, df)

        print("\nMarginal effects, percentage points:\n")
        print(effects[["label", "effect", "lower", "upper"]].round(2).to_string(index=False))

        fig_marginal_effects(effects)

        logger.info(f"🟢 Saved figure to {OUTPUT_DIR}")

    except Exception as e:
        logger.error(f"🔴 Failed to create Figure 4: {e}")


if __name__ == "__main__":
    config = load_model_config()

    generate_fig4(config)
