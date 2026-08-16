# Installation

## Requirements

- **Python 3.13** or newer (`requires-python = ">= 3.13"`)
- Network access for package install and for FIPS / NCSL data download
- Ability to manually download the CES file from [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/X11EP6) when prompted

## Recommended install (users)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install git+https://github.com/atunison3/capstone.git
```

Then run **from the directory where you want data stored**:

```bash
capstone
```

That creates (or reuses) `./.data/` in the current working directory and writes:

```text
.data/ces_data.csv
.data/fips.csv
.data/ncsl_voter_id_classification.csv
```

Data is **not** installed into `site-packages`. Always run `capstone` from a project folder you control.

### Windows quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install git+https://github.com/atunison3/capstone.git
capstone
```

### Configuration

Settings live in **`capstone/config.py`** (imported via `load_model_config()`). No external `config.toml` is required.

- Default relative data location: `.data`
- Resolved at runtime by `resolve_data_path()` so CLI downloads and loaders share one absolute path
- Details: [Configuration](documentation/configuration.md)

To customize column maps or use an absolute data directory, edit `capstone/config.py` in a source checkout and install editable (`pip install -e .`).

## Install from a local clone

### macOS / Linux

```bash
git clone https://github.com/atunison3/capstone.git
cd capstone
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
capstone
```

### Windows

```powershell
git clone https://github.com/atunison3/capstone.git
cd capstone
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
capstone
```

Editable install for development:

```bash
python -m pip install -e .
# or
python -m pip install -r requirements-dev.txt
```

## Runtime dependencies

Pinned in `pyproject.toml`:

| Package | Version |
| --- | --- |
| matplotlib | 3.10.9 |
| numpy | 2.5.1 |
| pandas | 3.0.3 |
| patsy | 1.0.2 |
| requests | 2.34.2 |
| scipy | 1.18.0 |
| statsmodels | 0.14.6 |

## Verify the install

```bash
python -c "import capstone; print('ok')"
python -c "from capstone.helper_functions import load_model_config; print(load_model_config()['data_path'])"
capstone
```

The second command prints the absolute data directory the pipeline will use (usually `<cwd>/.data`).

There is no `--help` flag on the CLI entry point. The command is `capstone`, which maps to `capstone.analysis:main` in `pyproject.toml`.

## Next

See [Usage](usage.md) for what the CLI does and how to call modules from Python.
