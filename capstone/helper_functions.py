import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from capstone import config

LOG_DIR = Path(".log")

# Directory containing this file: .../capstone/
PACKAGE_DIR = Path(__file__).resolve().parent
# Parent of the package: repo root in a source/editable tree, or site-packages when installed.
PACKAGE_PARENT = PACKAGE_DIR.parent

# Back-compat alias. Prefer detect_source_tree_root() / resolve_data_path().
PROJECT_ROOT = PACKAGE_PARENT


def detect_source_tree_root(start: Path = PACKAGE_PARENT) -> Path | None:
    """Return the repository root when the package is running from source/editable.

    A normal ``pip install`` places the package under ``site-packages``. In that
    case there is no project ``pyproject.toml`` next to the package, so this
    returns ``None`` and data paths should use the process cwd instead.
    """
    candidate = start.resolve()
    if (candidate / "pyproject.toml").is_file() and (candidate / "capstone").is_dir():
        return candidate
    return None


def resolve_data_path(
    data_path: Path | str,
    project_root: Path | None = None,
    *,
    cwd: Path | None = None,
) -> Path:
    """Resolve ``data_path`` for both source checkouts and installed wheels.

    - Absolute paths are expanded (``~``) and resolved as-is.
    - Relative paths prefer an existing directory under the process cwd (this is
      where ``setup_project`` writes ``Path(".data")`` for the ``capstone`` CLI).
    - If not found in cwd, an existing path under the source/editable repo root
      is used (so notebooks outside the repo root still find ``<repo>/.data``).
    - If nothing exists yet:
      - source/editable checkout → ``<repo>/<data_path>``
      - installed package → ``<cwd>/<data_path>``

    Never anchors relative paths at ``site-packages`` merely because the package
    was installed there.
    """
    path = Path(data_path).expanduser()
    if path.is_absolute():
        return path.resolve()

    cwd_path = (Path(cwd) if cwd is not None else Path.cwd()).resolve()
    cwd_candidate = (cwd_path / path).resolve()

    if project_root is not None:
        root: Path | None = Path(project_root).resolve()
    else:
        root = detect_source_tree_root()

    root_candidate = (root / path).resolve() if root is not None else None

    if cwd_candidate.exists():
        return cwd_candidate
    if root_candidate is not None and root_candidate.exists():
        return root_candidate

    # Default create/read location when the folder does not exist yet.
    if root_candidate is not None:
        return root_candidate
    return cwd_candidate


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
    default like ``.data`` works for:

    - ``pip install ...`` then ``capstone`` (uses cwd ``.data``)
    - notebooks/scripts in a source checkout (can use ``<repo>/.data``)
    """

    cfg = {name.lower(): value for name, value in vars(config).items() if name.isupper()}
    # if "data_path" in cfg:
    #     cfg["data_path"] = resolve_data_path(cfg["data_path"])
    return cfg
