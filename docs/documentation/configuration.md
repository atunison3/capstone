# Configuration

Configuration lives in the Python module **`capstone/config.py`**, not a TOML file.

`load_model_config()` imports that module and returns a dict of every **UPPERCASE** constant, with **lowercased** keys:

| Constant in config.py | Key in returned dict |
| --- | --- |
| `DATA_PATH` | `data_path` |
| `FULL_COLUMNS` | `full_columns` |
| `FEATURES` | `features` |
| … | … |

```python
from capstone.helper_functions import load_model_config

config = load_model_config()   # from capstone.config
print(config["data_path"])    # Path(".data")
print(config["target"])       # "Voted"
```

You can also import constants directly:

```python
from capstone.config import DATA_PATH, FEATURES, TARGET
```

## Top-level settings

| Key | Source constant | Role |
| --- | --- | --- |
| `data_path` | `DATA_PATH` | Directory for CES / FIPS / NCSL files (default `Path(".data")`) |
| `full_columns` | `FULL_COLUMNS` | Columns retained after CES cleaning |
| `categorical_features` | `CATEGORICAL_FEATURES` | Documented categorical feature list |
| `multiclass_features` | `MULTICLASS_FEATURES` | Multiclass feature list |
| `binary_features` | `BINARY_FEATURES` | Binary outreach feature list |
| `features` | `FEATURES` | Columns required non-null before modeling |
| `target` | `TARGET` | Outcome name (`"Voted"`) |

## Column rename maps

| Key | Source constant | Purpose |
| --- | --- | --- |
| `demographic_columns` | `DEMOGRAPHIC_COLUMNS` | CES demographic codes → readable names |
| `voter_outreach_columns` | `VOTER_OUTREACH_COLUMNS` | CES outreach items → readable names |
| `state_column` | `STATE_COLUMN` | CES state field → `State FIPS Code` |

## Value maps

`maps` (`MAPS`) pairs cleaned column names with the **lowercase name** of another config entry:

| Column | Mapping key |
| --- | --- |
| `Education` | `educ_mapping` (`EDUC_MAPPING`) |
| `Race` | `race_mapping` (`RACE_MAPPING`) |
| `Gender` | `gender_mapping` (`GENDER_MAPPING`) |
| `In person` | `in_person_mapping` (`IN_PERSON_MAPPING`) |
| `Phone call` | `phone_mapping` (`PHONE_MAPPING`) |
| `Email or text message` | `email_mapping` (`EMAIL_MAPPING`) |
| `Letter or postcard` | `letter_mapping` (`LETTER_MAPPING`) |

`clean_ces_data` applies each mapping with:

```python
df[column_name] = df[column_name].astype(str).replace(config[map_name])
```

## Changing configuration

Edit `capstone/config.py` and reinstall or use an editable install (`pip install -e .`) so the package picks up your changes.

To point at a different data directory, change:

```python
DATA_PATH = Path(".data")
```

## Expected files under `data_path`

```text
<data_path>/ces_data.csv
<data_path>/fips.csv
<data_path>/ncsl_voter_id_classification.csv
```
