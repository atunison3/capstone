import logging
import tomllib
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

LOCAL_CONFIG_PATH = Path("config.local.toml")
MODEL_CONFIG_PATH = Path("config.toml")
LOG_DIR = Path(".log")


def setup_logger(name: str = "capstone") -> logging.Logger:
    """Creates a logger that writes to the terminal and a rotating log file."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_DIR / "capstone.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


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
