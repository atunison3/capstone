# Installation

## Requirements

- **Python 3.13** or newer (`requires-python = ">= 3.13"`)
- Network access for package install and for FIPS / NCSL data download
- Ability to manually download the CES file from [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/X11EP6) when prompted

## Recommended install (users)

Install the package directly from GitHub:

```bash
pip install git+https://github.com/atunison3/capstone.git
```

Then run:

```bash
capstone
```

### Configuration

Settings live in **`capstone/config.py`** (imported via `load_model_config()`). No external `config.toml` is required. After `pip install`, those defaults are part of the installed package.

To customize data paths or column maps, edit `capstone/config.py` in a source checkout and install editable (`pip install -e .`), or change the constants in your environment’s installed copy.

## Install from a local clone

### macOS / Linux

```bash
git clone https://github.com/atunison3/capstone.git
cd capstone
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

### Windows

```powershell
git clone https://github.com/atunison3/capstone.git
cd capstone
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
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
capstone
```

There is no `--help` flag on the CLI entry point. The command is `capstone`, which maps to `capstone.analysis:main` in `pyproject.toml`.

## Next

See [Usage](getting-started/usage.md) for what the CLI does and how to call modules from Python.
