# Usage

## Quick start

```bash
pip install git+https://github.com/atunison3/capstone.git
capstone
```

Configuration comes from `capstone.config` (no separate config file required).

## What the CLI runs

The console script is defined as:

```toml
[project.scripts]
capstone = "capstone.analysis:main"
```

`capstone.analysis.main` performs this pipeline:

1. **Download / install data**
   - `download_ces_data()` — interactive CES install into `.data/ces_data.csv`
   - `download_state_data()` — Census FIPS state table into `.data/fips.csv`
   - `install_ncsl_classification()` — NCSL voter ID classes into `.data/ncsl_voter_id_classification.csv`
2. **Load config** — `load_model_config()` reads UPPERCASE constants from `capstone.config`
3. **Clean and merge** — `load_full_dataframe(config)`
4. **Fit model** — `train_model(df)` and print `model.summary()`

Logs go to the console (INFO+) and to `.log/capstone.log`.

## CES download note

Automated CES download is blocked by Harvard Dataverse WAF protections. When CES data is missing, the tool prints instructions, waits for you to place the expected CSV in your user `Downloads` folder, then copies it to `.data/ces_data.csv`.

Expected download filename (default):

```text
CCES24_Common_OUTPUT_vv_topost_final.csv
```

Source page used by the installer:

```text
https://dataverse.harvard.edu/file.xhtml?fileId=12050325&version=9.0
```

## Python API examples

### Run the full analysis pipeline

```python
from capstone.analysis import main

main()
```

### Load cleaned analysis data only

```python
from capstone.helper_functions import load_model_config
from capstone.data_cleaning import load_full_dataframe

config = load_model_config()  # from capstone.config
df = load_full_dataframe(config)
print(df.head())
```

### Fit the logistic regression

```python
from capstone.helper_functions import load_model_config
from capstone.data_cleaning import load_full_dataframe
from capstone.logistic_regression import train_model

config = load_model_config()
df = load_full_dataframe(config)
model = train_model(df)
print(model.summary())
```

### Install project data without fitting a model

```python
from capstone.setup_project import main as setup_data

setup_data()  # writes under .data/ by default
```

Or as a module:

```bash
python -m capstone.setup_project
```

(`setup_project` is runnable via `python capstone/setup_project.py` from a source checkout as well.)

## Generate report figures

Figure scripts live under `capstone/visualization/` and write PNGs to `docs/assets/` (anchored to the repository root).

From a source checkout with data under `DATA_PATH` (default `.data/`):

```bash
python capstone/visualization/report_fig1_real.py
python capstone/visualization/report_fig2_real.py
python capstone/visualization/report_fig3_real.py
python capstone/visualization/report_fig4_real.py
```

| Script | Output |
| --- | --- |
| `report_fig1_real.py` | `docs/assets/report_fig1_turnout_by_strictness.png` |
| `report_fig2_real.py` | `docs/assets/report_fig2_turnout_by_contacted.png` |
| `report_fig3_real.py` | `docs/assets/report_fig3_turnout_by_contacted.png` |
| `report_fig4_real.py` | `docs/assets/report_fig4_logistic_marginal_effects.png` |

## Working directory layout after a run

```text
.
├── .data/               # default DATA_PATH from capstone.config
│   ├── ces_data.csv
│   ├── fips.csv
│   └── ncsl_voter_id_classification.csv
└── .log/
    └── capstone.log
```
