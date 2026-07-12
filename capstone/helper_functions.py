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


def load_voter_id_effect() -> DataFrame:
    """
    Function to get the voter photo ID strictness data

    California = 1
    Washington = 2
    Idaho = 3
    Wyoming = 4
    Kansas = 5
    """

    df = load_fips_data()
    df.set_index("State")

    # df.loc["ALABAMA", "Voter ID Law"] = 3
    # df.loc["ALASKA", "Voter ID Law"] = 2
    # df.loc["ARIZONA", "Voter ID Law"] = 4
    # df.loc["ARKANSAS", "Voter ID Law"] = 5
    # df.loc["CALIFORNIA", "Voter ID Law"] = 1
    # df.loc["COLORADO", "Voter ID Law"] = 2
    # df.loc["CONNECTICUT", "Voter ID Law"] = 1
    # df.loc["DELAWARE", "Voter ID Law"] =
    # df.loc["DISTRICT OF COLUMBIA", "Voter ID Law"] =
    # df.loc["FLORIDA", "Voter ID Law"] =
    # df.loc["GEORGIA", "Voter ID Law"] =
    # df.loc["HAWAII", "Voter ID Law"] =
    # df.loc["IDAHO", "Voter ID Law"] =
    # df.loc["ILLINOIS", "Voter ID Law"] =
    # df.loc["INDIANA", "Voter ID Law"] =
    # df.loc["IOWA", "Voter ID Law"] =
    # df.loc["KANSAS", "Voter ID Law"] =
    # df.loc["KENTUCKY", "Voter ID Law"] =
    # df.loc["LOUISIANA", "Voter ID Law"] =
    # df.loc["MAINE", "Voter ID Law"] =
    # df.loc["MARYLAND", "Voter ID Law"] =
    # df.loc["MASSACHUSETTS", "Voter ID Law"] =
    # df.loc["MICHIGAN", "Voter ID Law"] =
    # df.loc["MINNESOTA", "Voter ID Law"] =
    # df.loc["MISSISSIPPI", "Voter ID Law"] =
    # df.loc["MISSOURI", "Voter ID Law"] =
    # df.loc["MONTANA", "Voter ID Law"] =
    # df.loc["NEBRASKA", "Voter ID Law"] =
    # df.loc["NEVADA", "Voter ID Law"] =
    # df.loc["NEW HAMPSHIRE", "Voter ID Law"] =
    # df.loc["NEW JERSEY", "Voter ID Law"] =
    # df.loc["NEW MEXICO", "Voter ID Law"] =
    # df.loc["NEW YORK", "Voter ID Law"] =
    # df.loc["NORTH CAROLINA", "Voter ID Law"] =
    # df.loc["NORTH DAKOTA", "Voter ID Law"] =
    # df.loc["OHIO", "Voter ID Law"] =
    # df.loc["OKLAHOMA", "Voter ID Law"] =
    # df.loc["OREGON", "Voter ID Law"] =
    # df.loc["PENNSYLVANIA", "Voter ID Law"] =
    # df.loc["RHODE ISLAND", "Voter ID Law"] =
    # df.loc["SOUTH CAROLINA", "Voter ID Law"] =
    # df.loc["SOUTH DAKOTA", "Voter ID Law"] =
    # df.loc["TENNESSEE", "Voter ID Law"] =
    # df.loc["TEXAS", "Voter ID Law"] =
    # df.loc["UTAH", "Voter ID Law"] =
    # df.loc["VERMONT", "Voter ID Law"] =
    # df.loc["VIRGINIA", "Voter ID Law"] =
    # df.loc["WASHINGTON", "Voter ID Law"] =
    # df.loc["WEST VIRGINIA", "Voter ID Law"] =
    # df.loc["WISCONSIN", "Voter ID Law"] =
    # df.loc["WYOMING", "Voter ID Law"] =

    df = DataFrame()
    return df


if __name__ == "__main__":

    fips_df = load_fips_data()
    print(fips_df.head())
