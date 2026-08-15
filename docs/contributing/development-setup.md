# Development Setup

## Clone the repository

```bash
git clone https://github.com/atunison3/capstone.git
cd capstone
```

## Create and activate a virtual environment

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Use Python 3.13+.

## Install the project for development

The repo provides `requirements.txt`.

```bash
python -m pip install -r requirements.txt
```

Editable install only:

```bash
python -m pip install -e .
```

Editable mode means changes under `capstone/` are picked up without reinstalling after each edit.

## Pre-commit hooks

The repository includes `.pre-commit-config.yaml` with hooks for:

- trailing whitespace
- Black (`capstone`, `tests`)
- Ruff (`capstone`, `tests`)
- Bandit
- MyPy (`capstone`, `tests`)
- `python -m unittest discover -s tests -v`

If you use pre-commit:

```bash
pre-commit install
pre-commit run --all-files
```

## Branching and pull requests

```bash
git checkout -b <branch-name>
# ... edit ...
git add .
git commit -m "Describe the change"
git push origin <branch-name>
```

Open a PR into `main`. CI runs on pushes and on PRs to `main` (see `.github/workflows`). PR's require approval from one or more other contributor and all comments to be resolved.

## Data for local runs

From the project root (configuration comes from `capstone/config.py`):

```bash
capstone
```

or:

```bash
python -m capstone.setup_project
```

CES still requires the manual Dataverse download step the first time.
