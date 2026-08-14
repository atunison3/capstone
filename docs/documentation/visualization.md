# Visualization

Package: `capstone.visualization`

Shared plot styling plus scripts that write report figures into `docs/assets/`.

## Visuals module

Module: `capstone.visualization.visuals`

### `ColorScheme`

`StrEnum` of University of Michigan palette colors used across figures (for example `UM_BLUE`, `UM_MAIZE`, `TAPPAN_RD`).

### `OUTPUT_DIR`

Absolute path to `<repo>/docs/assets`, resolved from `visuals.py` via `__file__` so figure scripts still write to the docs site when launched from another working directory.

### `ensure_output_dir`

```python
ensure_output_dir(path: Path = OUTPUT_DIR) -> Path
```

Creates the output directory with `parents=True, exist_ok=True` and returns it.

### `compute_turnout_by_category`

```python
compute_turnout_by_category(
    df: DataFrame,
    category: str,
    order: list[str],
) -> DataFrame
```

Groups `df` by `category` and computes:

| Column | Meaning |
| --- | --- |
| `n` | group size |
| `pct` | mean of `Voted` × 100 |
| `ci` | 95% Wald CI for the percentage |

Rows are reindexed to `order`.

### Shared style

`PLT_PARAMS` is a matplotlib rc dictionary (DPI, fonts, spine visibility, UM blue text colors). `Y_LABEL` is `"Validated turnout (%)"`.

## Report figure scripts

Each script loads config + cleaned data, builds a figure, and saves a PNG under `docs/assets/`.

| Module | Generator | Output file |
| --- | --- | --- |
| `report_fig1_real` | `generate_fig1` | `report_fig1_turnout_by_strictness.png` |
| `report_fig2_real` | `generate_fig2` | `report_fig2_turnout_by_contacted.png` |
| `report_fig3_real` | `generate_fig3` | `report_fig3_turnout_by_contacted.png` |
| `report_fig4_real` | `generate_fig4` | `report_fig4_logistic_marginal_effects.png` |

### Figure 1 — turnout by voter ID strictness

Bar chart of validated turnout by NCSL classification with 95% CIs.

### Figure 2 — turnout by any contact

Compares contacted vs not contacted respondents (any of in-person, phone, email/text, letter/postcard).

### Figure 3 — turnout by contact channel

Turnout breakdown across outreach channels.

### Figure 4 — logistic marginal effects

Uses the fitted logit from `train_model` and plots average marginal probability contrasts for outreach terms (including interactions with NCSL classification where computed by the script).

### Example

```bash
python capstone/visualization/report_fig2_real.py
```

```python
from capstone.helper_functions import load_model_config
from capstone.visualization.report_fig2_real import generate_fig2

generate_fig2(load_model_config())
```

## Note on `mke_um_figs.py`

`capstone/visualization/mke_um_figs.py` is excluded from Ruff via `pyproject.toml` `extend-exclude` and is not part of the primary report pipeline documented here.
