# Project Setup

Module: `capstone.setup_project`

Creates `.data/` (by default) and installs the three external inputs the analysis needs.

## Defaults

```python
OUTPUT_DIR = Path(".data")
```

## `get_user_downloads_folder`

```python
get_user_downloads_folder() -> Path
```

Returns `Path.home() / "Downloads"`.

## `create_data_directory`

```python
create_data_directory(output_dir: Path = OUTPUT_DIR) -> None
```

Creates `output_dir` with `parents=True, exist_ok=True`.

## `download_ces_data`

```python
download_ces_data(
    output_dir: Path = OUTPUT_DIR,
    filename: str = "CCES24_Common_OUTPUT_vv_topost_final.csv",
) -> None
```

Installs CES data as `{output_dir}/ces_data.csv`.

Behavior:

- If `ces_data.csv` already exists, returns immediately.
- Otherwise prints instructions for a **manual** download from Harvard Dataverse (automated access is blocked by WAF protections).
- Looks for `filename` in the user Downloads folder and moves/copies it to `.data/ces_data.csv`.

## `download_state_data`

```python
download_state_data(output_dir: Path = OUTPUT_DIR) -> None
```

Downloads Census state FIPS information and writes `{output_dir}/fips.csv`. State data is requested from <https://www2.census.gov/geo/docs/reference/state.txt>.

## `install_ncsl_classification`

```python
install_ncsl_classification(
    output_dir: Path = OUTPUT_DIR,
    filename: str = "ncsl_voter_id_classification.csv",
) -> None
```

Builds or refreshes NCSL voter ID classification data and writes. Data is manually transcribed from <https://www.ncsl.org/elections-and-campaigns/voter-id#12539>.

```text
{output_dir}/ncsl_voter_id_classification.csv
```

## `main`

```python
main(output_dir: Path = OUTPUT_DIR) -> None
```

Runs the full data setup sequence:

1. `create_data_directory`
2. `download_ces_data`
3. `download_state_data`
4. `install_ncsl_classification`

### Example

```python
from capstone.setup_project import main

main()
```
