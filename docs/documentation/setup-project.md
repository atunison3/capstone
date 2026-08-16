# Project Setup

Module: `capstone.setup_project`

Installs the three external inputs the analysis needs into the **resolved data directory** (same location `load_model_config()["data_path"]` uses).

## Defaults

```python
from capstone.config import DATA_PATH
from capstone.helper_functions import resolve_data_path

def default_output_dir() -> Path:
    return resolve_data_path(DATA_PATH)
```

- `OUTPUT_DIR = Path(".data")` remains as a backward-compatible constant.
- Callables default `output_dir=None` and resolve via `default_output_dir()` at runtime.
- After `pip install`, that is typically **`<cwd>/.data`**, not a path under `site-packages`.

See [Configuration](documentation/configuration.md) for the full resolution rules.

## `get_user_downloads_folder`

```python
get_user_downloads_folder() -> Path
```

Returns `Path.home() / "Downloads"`.

## `default_output_dir`

```python
default_output_dir() -> Path
```

Returns the absolute data directory shared by installers and loaders.

## `create_data_directory`

```python
create_data_directory(output_dir: Path | None = None) -> None
```

Creates `output_dir` (or `default_output_dir()` when omitted) with `parents=True, exist_ok=True`.

## `download_ces_data`

```python
download_ces_data(
    output_dir: Path | None = None,
    filename: str = "CCES24_Common_OUTPUT_vv_topost_final.csv",
) -> None
```

Installs CES data as `{output_dir}/ces_data.csv`.

Behavior:

- If `ces_data.csv` already exists, returns immediately.
- Otherwise prints instructions for a **manual** download from Harvard Dataverse (automated access is blocked by WAF protections).
- Looks for `filename` in the user Downloads folder and moves it into `{output_dir}/ces_data.csv`.
- Rewrites the CSV once after the move to normalize it.

## `download_state_data`

```python
download_state_data(output_dir: Path | None = None) -> None
```

Downloads Census state FIPS information and writes `{output_dir}/fips.csv`.

Source: [Census state FIPS reference](https://www2.census.gov/geo/docs/reference/state.txt).

Skips the download when `fips.csv` already exists.

## `install_ncsl_classification`

```python
install_ncsl_classification(
    output_dir: Path | None = None,
    filename: str = "ncsl_voter_id_classification.csv",
) -> None
```

Writes state-level NCSL voter ID classifications (manually curated table) to:

```text
{output_dir}/ncsl_voter_id_classification.csv
```

Skips when the file already exists. Classification text is based on NCSL voter ID materials:
[NCSL voter ID](https://www.ncsl.org/elections-and-campaigns/voter-id#12539).

## `main`

```python
main(output_dir: Path | None = None) -> None
```

Runs the full data setup sequence against one resolved directory:

1. Resolve `output_dir` (`default_output_dir()` when omitted) and log it
2. `create_data_directory`
3. `download_ces_data`
4. `download_state_data`
5. `install_ncsl_classification`

### Example

```python
from capstone.setup_project import main, default_output_dir

print(default_output_dir())
main()  # installs into that directory
```

### CLI / package entry

The `capstone` command calls these download helpers with no `output_dir`, so they use `default_output_dir()` — the same path later used by `load_model_config()["data_path"]`.
