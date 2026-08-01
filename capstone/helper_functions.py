import tomllib
from pathlib import Path
from typing import Any

LOCAL_CONFIG_PATH = Path("config.local.toml")
MODEL_CONFIG_PATH = Path("config.toml")


def expand_user(path: Path) -> Path:
    """Expands the user's path"""

    data_path = Path(path).expanduser().resolve()

    if not data_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {data_path}")

    return data_path


def get_data_path(config_path: Path = LOCAL_CONFIG_PATH) -> Path:
    """Loads the local config and extracts the data path"""

    # Load the user's local config
    config = load_model_config(config_path)

    # Extract the data_path into a Path object
    data_path = Path(config["data_path"])

    return data_path


def load_local_config(config_path: Path = LOCAL_CONFIG_PATH) -> dict[Any, Any]:
    """Loads the local config"""

    # Generically load the config
    config = load_model_config(config_path)

    # The local config requires the data path
    if "data_path" not in config:
        raise KeyError(
            "Required configuration setting 'data_path' is missing."
            "Please add a 'data_path' with a path to your CES data into "
            "config.local.toml"
        )

    return config


def load_model_config(config_path: Path = MODEL_CONFIG_PATH) -> dict[Any, Any]:
    """Loads the model  config"""

    path = expand_user(config_path)

    if not path.is_file():
        raise IsADirectoryError(f"Configuration path is not a file: {path}")

    with path.open("rb") as file:
        config: dict[Any, Any] = tomllib.load(file)

    return config
