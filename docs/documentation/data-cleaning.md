# Data Cleaning

Module: `capstone.data_cleaning`

Loads CES, FIPS, and NCSL inputs, renames and maps CES fields using `capstone.config` (via the dict from `load_model_config()`), builds a validated turnout outcome, and returns a modeling-ready frame.

Default on-disk data root: `.data/` (overridden by `config["data_path"]` in `load_full_dataframe`).

## `load_dataframe`

```python
load_dataframe(data_path: Path = DATA_PATH) -> DataFrame
```

Reads `{data_path}/ces_data.csv`.

## `load_fips_data`

```python
load_fips_data(data_path: Path = DATA_PATH) -> DataFrame
```

Reads `{data_path}/fips.csv`, casts key columns, and renames them to:

- `State FIPS Code`
- `State Name`
- `State Code`

## `load_voter_id_effect`

```python
load_voter_id_effect(data_path: Path) -> DataFrame
```

Reads `{data_path}/ncsl_voter_id_classification.csv`.

## `rename_columns`

```python
rename_columns(df: DataFrame, column_map: dict[str, str]) -> DataFrame
```

Returns a copy of `df` with columns renamed according to `column_map`.

## `merge_fips_ncsl`

```python
merge_fips_ncsl(fips_df: DataFrame, ncsl_df: DataFrame) -> DataFrame
```

Inner-merges FIPS and NCSL tables on `State Name`. Returns:

```text
State Name | State Code | NCSL Classification | State FIPS Code
```

## `clean_ces_data`

```python
clean_ces_data(df: DataFrame, config: dict[Any, Any]) -> DataFrame
```

Cleaning steps:

1. Rename demographic, outreach, and state columns from config maps.
2. Drop rows missing `TS_voterstatus`.
3. Create `Voted` as `(TS_g2024 != 7).astype(int)` (7 = did not vote).
4. Create `Age` as `2024 - Birth Year`.
5. Map coded columns through `config["maps"]` / mapping tables.
6. Keep only `config["full_columns"]`.

## `merge_ces_fips`

```python
merge_ces_fips(ces_df: DataFrame, merged_fips_nscl: DataFrame) -> DataFrame
```

Merges cleaned CES rows onto state metadata using `State FIPS Code`.

## `load_full_dataframe`

```python
load_full_dataframe(config: dict[Any, Any]) -> DataFrame
```

Full load path used by the CLI and figure scripts:

1. Resolve `data_path` from config.
2. Load and clean CES.
3. Load FIPS and NCSL; merge them.
4. Merge onto CES.
5. Drop rows with missing values in `config["features"]`.

### Example

```python
from capstone.helper_functions import load_model_config
from capstone.data_cleaning import load_full_dataframe

config = load_model_config()
df = load_full_dataframe(config)
```

## `main`

```python
main() -> DataFrame
```

Loads `capstone.config` via `load_model_config()` and returns `load_full_dataframe(config)`. Runnable as a script for a quick data preview (`print` of head and dtypes).
