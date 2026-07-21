import pandas as pd
import requests
from io import StringIO
from pandas import DataFrame
from pathlib import Path

from capstone.helper_functions import load_config, expand_user


def load_dataframe(ces_path: Path) -> DataFrame:
    """Loads the CES data"""

    csv_path = ces_path / "data.csv"
    df = pd.read_csv(csv_path)

    return df


def load_fips_data(data_path: Path) -> DataFrame:
    """Loads FIPS data"""

    # Expand the data path
    data_path = expand_user(data_path)
    if not data_path.is_dir():
        raise NotADirectoryError(f"Data path is not a directory: {data_path}")

    # Verify the data path exists
    data_path.mkdir(parents=True, exist_ok=True)

    # Determine the fips.csv path
    fips_path = data_path / "fips.csv"

    # Determine if user already has the fips data saved
    if fips_path.exists():
        return pd.read_csv(
            fips_path,
            dtype={"inputstate": "string"},
        )

    # URL for the fips data
    url = "https://www2.census.gov/geo/docs/reference/state.txt"

    # Request the fips data
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    df = pd.read_csv(
        StringIO(resp.text),
        sep="|",
        dtype={
            "STATE": "string",
            "STUSAB": "string",
            "STATE_NAME": "string",
            "STATENS": "string",
        },
    )

    # Save the dataframe so we don't need to request it next time
    df.to_csv(fips_path, index=False)

    return df


def rename_columns(df: DataFrame, column_map: dict[str, str]) -> DataFrame:
    """Renames dataframe columns"""

    df = df.rename(columns=column_map)

    return df


if __name__ == "__main__":

    # Get the data path
    config = load_config()
    data_path = Path(config["data_path"]) / "dev"

    # Load the dataframe
    df = load_dataframe(data_path)
    print(df.head())

    fips_df = load_fips_data(data_path)
    print(fips_df.head())
