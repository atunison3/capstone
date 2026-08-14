# Documentation

Detailed reference for the `capstone` Python package (University of Michigan MADS Capstone 2026).

## Package layout

```text
capstone/
├── analysis.py              # CLI entry point (capstone command)
├── data_cleaning.py         # Load, clean, and merge analysis data
├── logistic_regression.py   # Turnout logit model
├── setup_project.py         # Data acquisition into .data/
├── helper_functions.py      # Logging and config loading
└── visualization/           # Report figure generators
    ├── visuals.py
    ├── report_fig1_real.py
    ├── report_fig2_real.py
    ├── report_fig3_real.py
    └── report_fig4_real.py
```

## Contents

| Page | Description |
| --- | --- |
| [Analysis CLI](documentation/analysis.md) | `capstone` command and `analysis.main` |
| [Data Cleaning](documentation/data-cleaning.md) | CES / FIPS / NCSL load and merge |
| [Logistic Regression](documentation/logistic-regression.md) | Model formula and training |
| [Project Setup](documentation/setup-project.md) | Downloading and installing input data |
| [Helper Functions](documentation/helper-functions.md) | Logger and `capstone.config` loader |
| [Visualization](documentation/visualization.md) | Shared styling and report figures |
| [Configuration](documentation/configuration.md) | `capstone/config.py` constants and keys |

## Pipeline overview

```text
capstone/config.py
    │
    ▼
setup_project ──► .data/ (ces_data.csv, fips.csv, ncsl_…)
    │
    ▼
data_cleaning.load_full_dataframe
    │
    ├──► logistic_regression.train_model
    │
    └──► visualization.report_fig*_real
```

The public CLI (`capstone`) runs setup → cleaning → model fit. Figure scripts are separate entry points intended for report generation from a source checkout.
