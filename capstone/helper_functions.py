import logging
import tomllib
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

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


def load_model_config(config_path: Path = MODEL_CONFIG_PATH) -> dict[Any, Any]:
    """Loads the model  config"""

    path = expand_user(config_path)

    if not path.is_file():
        raise IsADirectoryError(f"Configuration path is not a file: {path}")

    with path.open("rb") as file:
        config: dict[Any, Any] = tomllib.load(file)

    return config
