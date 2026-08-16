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
pip install -U git+https://github.com/atunison3/capstone.git
```

Run **from the directory where you want data stored**. Prefer the module form so the active interpreter cannot be confused with another install:

```bash
python -m capstone
```

The console script also works when it points at this venv:

```bash
which capstone
head -n 1 "$(which capstone)"   # must be this venv's python
capstone
```

### If PATH still has a global install

A previous `pip install` under another Python (for example 3.14) may leave:

```text
/Library/Frameworks/Python.framework/Versions/3.14/bin/capstone
```

Uninstall leftovers and prefer `python -m capstone`:

```bash
python3.14 -m pip uninstall -y capstone-2026   # if installed
hash -r                                       # bash; or open a new shell
python -m capstone
```

That creates (or reuses) `./.data/` in the current working directory and writes:

```text
.data/ces_data.csv
.data/fips.csv
.data/ncsl_voter_id_classification.csv
```

Data is **not** stored under `site-packages`. Startup logs print the Python executable, package file location, and resolved data directory — confirm none of them point at an unexpected global install.

### Windows quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -U git+https://github.com/atunison3/capstone.git
python -m capstone
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
python -m pip install -e .
python -m capstone
```

### Windows

```powershell
git clone https://github.com/atunison3/capstone.git
cd capstone
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m capstone
```

Development dependencies:

```bash
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
python -c "import capstone, sys; print(sys.executable); print(capstone.__file__)"
python -c "from capstone.helper_functions import load_model_config; print(load_model_config()['data_path'])"
python -m capstone
```

You should see:

- `sys.executable` inside your `.venv`
- `capstone.__file__` under that venv (or an editable source tree)
- `data_path` as `<cwd>/.data` — **never** `.../site-packages/.data`

There is no `--help` flag. Entry points: `capstone` → `capstone.analysis:main`, and `python -m capstone`.

## Next

See [Usage](usage.md) for what the CLI does and how to call modules from Python.
