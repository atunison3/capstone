import pandas as pd
import tomllib
from pandas import DataFrame
from pathlib import Path


def load_ces_data(data_path: Path) -> DataFrame:
    """Loads the CES data"""

    df = pd.read_csv(data_path)

    return df


def load_config(config_path: Path = Path("config.toml")) -> dict:
    """Loads the configuration"""

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if not config_path.is_file():
        raise IsADirectoryError(f"Expected a file, got: {config_path}")

    with config_path.open("rb") as file:
        return tomllib.load(file)
