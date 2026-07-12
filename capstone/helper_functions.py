import pandas as pd
import re
import requests
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


def load_fips_data() -> DataFrame:
    """Loads FIPS data"""

    url = "https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt"

    resp = requests.get(url, timeout=30)

    pattern = r"^\s*(\d{2})\s+([A-Z]+(?:\s+[A-Z]+)*)\s*$"

    matches = re.findall(pattern, resp.text, flags=re.MULTILINE)

    df = pd.DataFrame(matches, columns=["FIPS", "State"])

    return df


if __name__ == "__main__":

    fips_df = load_fips_data()
    print(fips_df.head())
