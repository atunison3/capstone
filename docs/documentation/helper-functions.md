# Helper Functions

Module: `capstone.helper_functions`

Shared utilities for logging and configuration.

## Constants

```python
LOG_DIR = Path(".log")
```

Log paths are relative to the process current working directory.

## `setup_logger`

```python
setup_logger(name: str = "capstone") -> logging.Logger
```

Creates a logger that writes to:

- the terminal at INFO level
- a rotating file at `.log/capstone.log` (5 MB × 5 backups) at DEBUG level

If handlers already exist on the named logger, the existing logger is returned unchanged.

### Example

```python
from capstone.helper_functions import setup_logger

logger = setup_logger()
logger.info("pipeline start")
```

## `expand_user`

```python
expand_user(path: Path) -> Path
```

Expands `~`, resolves the path, and raises `FileNotFoundError` if it does not exist.

## `load_model_config`

```python
load_model_config() -> dict[str, Any]
```

Loads configuration from **`capstone.config`**.

Returns a new `dict` whose keys are the lowercased names of every UPPERCASE constant in that module, and whose values are the constant values themselves.

### Example

```python
from capstone.helper_functions import load_model_config

config = load_model_config()
print(config["data_path"])
print(config["features"])
```

See [Configuration](documentation/configuration.md) for keys and constants.
