import tomllib
from pathlib import Path
from typing import Any

LOCAL_CONFIG_PATH = Path("config.local.toml")


def load_config(config_path: Path = LOCAL_CONFIG_PATH) -> dict[Any, Any]:
    """Loads the local config"""

    path = Path(config_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    if not path.is_file():
        raise IsADirectoryError(f"Configuration path is not a file: {path}")

    with path.open("rb") as file:
        config: dict[Any, Any] = tomllib.load(file)

    if "data_path" not in config:
        raise KeyError(
            "Required configuration seeting 'data_path' is missing."
            "Please add a 'data_path' with a path to your CES data into "
            "config.local.toml"
        )

    return config
