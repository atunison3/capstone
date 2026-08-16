import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from capstone import config

LOG_DIR = Path(".log")

# Repository root: .../capstone/helper_functions.py -> parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_data_path(data_path: Path | str, project_root: Path = PROJECT_ROOT) -> Path:
    """Resolve ``data_path`` so notebooks/scripts work outside the repo root.

    - Absolute paths are expanded (``~``) and resolved as-is.
    - Relative paths are resolved against ``project_root`` (the install/source
      tree that contains the ``capstone`` package), not the process cwd.
    """
    path = Path(data_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (project_root / path).resolve()


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


def load_model_config() -> dict[str, Any]:
    """Load configuration from ``capstone.config``.

    Returns a dict of every UPPERCASE constant in ``capstone.config``, with
    lowercased keys (for example ``DATA_PATH`` → ``"data_path"``).

    ``data_path`` is normalized with :func:`resolve_data_path` so a relative
    default like ``.data`` points at ``<project_root>/.data`` even when the
    caller is a notebook or script whose cwd is not the repository root.
    """

    cfg = {name.lower(): value for name, value in vars(config).items() if name.isupper()}
    # if "data_path" in cfg:
    #     cfg["data_path"] = resolve_data_path(cfg["data_path"])
    return cfg
