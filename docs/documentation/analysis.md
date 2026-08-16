# Analysis CLI

Module: `capstone.analysis`

This module is the package entry point wired in `pyproject.toml`:

```toml
[project.scripts]
capstone = "capstone.analysis:main"
```

## `main`

```python
main() -> None
```

Runs the end-to-end analysis pipeline:

1. `download_ces_data()` — into `default_output_dir()` / resolved data path
2. `download_state_data()`
3. `install_ncsl_classification()`
4. `load_model_config()` — resolves absolute `data_path`
5. `load_full_dataframe(config)` — reads from that same `data_path`
6. `train_model(df)`
7. `calculate_probabilities(model)` — prints `summary2()` with an **Expit** column

### Example

```bash
capstone
```

```python
from capstone.analysis import main

main()
```

### Notes

- Loads settings from `capstone.config` via `load_model_config()`.
- Data installers and loaders share `resolve_data_path()` / `default_output_dir()` (typically `<cwd>/.data` after `pip install`).
- Logs under `<cwd>/.log/`.
- Does not accept CLI arguments.
- Model reporting uses `calculate_probabilities` from `capstone.logistic_regression` (not raw `model.summary()`), so coefficient tables include Expit values. See [Logistic Regression](documentation/logistic-regression.md).
- Path rules: [Configuration](documentation/configuration.md).
