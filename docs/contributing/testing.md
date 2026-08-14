# Testing and Quality Checks

## Unit tests

The project uses Python's standard `unittest` runner. Tests live in `tests/`.

```bash
python -m unittest discover -s tests -v
```

CI uses the same discovery command without `-v`:

```bash
python -m unittest discover -s tests
```

## Linting and formatting

Commands used in the README / pre-commit configuration:

```bash
black .
ruff check
bandit .
mypy .
```

Pre-commit scopes Black and Ruff to `capstone` and `tests`:

```bash
black capstone tests
ruff check capstone tests
bandit -r capstone tests
mypy capstone tests
```

Ruff and Black both use `line-length = 120` from `pyproject.toml`.

## GitHub Actions

`.github/workflows` runs on pushes to any branch and on pull requests to `main`:

1. Install `requirements-dev.txt`
2. `ruff check`
3. `bandit -r .`
4. `mypy .`
5. `python -m unittest discover -s tests`

## Suggested local checklist before a PR

```bash
black capstone tests
ruff check capstone tests
mypy capstone tests
bandit -r capstone tests
python -m unittest discover -s tests -v
```
