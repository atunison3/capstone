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

    df = pd.DataFrame(matches, columns=["inputstate", "state_name"])

    return df


def load_voter_id_effect() -> DataFrame:
    """
    Function to get the voter photo ID strictness data from
    https://www.ncsl.org/elections-and-campaigns/voter-id#12539

    For reference, I am on the understanding this is true:
    California = 1
    Washington = 2
    Idaho = 3
    Wyoming = 4
    Kansas = 5
    """

    df = load_fips_data()
    df = df.set_index("state_name")

    # Fill in states from image
    df.loc["ALABAMA", "Voter ID Law"] = 3
    df.loc["ALASKA", "Voter ID Law"] = 2
    df.loc["ARIZONA", "Voter ID Law"] = 4
    df.loc["ARKANSAS", "Voter ID Law"] = 5
    df.loc["CALIFORNIA", "Voter ID Law"] = 1
    df.loc["COLORADO", "Voter ID Law"] = 2
    df.loc["CONNECTICUT", "Voter ID Law"] = 2
    df.loc["DELAWARE", "Voter ID Law"] = 2
    df.loc["DISTRICT OF COLUMBIA", "Voter ID Law"] = 0  # Is this on the map?
    df.loc["FLORIDA", "Voter ID Law"] = 3
    df.loc["GEORGIA", "Voter ID Law"] = 5
    df.loc["HAWAII", "Voter ID Law"] = 1
    df.loc["IDAHO", "Voter ID Law"] = 3
    df.loc["ILLINOIS", "Voter ID Law"] = 1
    df.loc["INDIANA", "Voter ID Law"] = 5
    df.loc["IOWA", "Voter ID Law"] = 2
    df.loc["KANSAS", "Voter ID Law"] = 5
    df.loc["KENTUCKY", "Voter ID Law"] = 3
    df.loc["LOUISIANA", "Voter ID Law"] = 3
    df.loc["MAINE", "Voter ID Law"] = 1
    df.loc["MARYLAND", "Voter ID Law"] = 1
    df.loc["MASSACHUSETTS", "Voter ID Law"] = 1
    df.loc["MICHIGAN", "Voter ID Law"] = 3
    df.loc["MINNESOTA", "Voter ID Law"] = 1
    df.loc["MISSISSIPPI", "Voter ID Law"] = 5
    df.loc["MISSOURI", "Voter ID Law"] = 3
    df.loc["MONTANA", "Voter ID Law"] = 3
    df.loc["NEBRASKA", "Voter ID Law"] = 3
    df.loc["NEVADA", "Voter ID Law"] = 1
    df.loc["NEW HAMPSHIRE", "Voter ID Law"] = 5
    df.loc["NEW JERSEY", "Voter ID Law"] = 1
    df.loc["NEW MEXICO", "Voter ID Law"] = 1
    df.loc["NEW YORK", "Voter ID Law"] = 1
    df.loc["NORTH CAROLINA", "Voter ID Law"] = 5
    df.loc["NORTH DAKOTA", "Voter ID Law"] = 3
    df.loc["OHIO", "Voter ID Law"] = 5
    df.loc["OKLAHOMA", "Voter ID Law"] = 2
    df.loc["OREGON", "Voter ID Law"] = 1
    df.loc["PENNSYLVANIA", "Voter ID Law"] = 1
    df.loc["RHODE ISLAND", "Voter ID Law"] = 3  # Maybe?
    df.loc["SOUTH CAROLINA", "Voter ID Law"] = 3
    df.loc["SOUTH DAKOTA", "Voter ID Law"] = 3
    df.loc["TENNESSEE", "Voter ID Law"] = 5
    df.loc["TEXAS", "Voter ID Law"] = 3
    df.loc["UTAH", "Voter ID Law"] = 2
    df.loc["VERMONT", "Voter ID Law"] = 1
    df.loc["VIRGINIA", "Voter ID Law"] = 2
    df.loc["WASHINGTON", "Voter ID Law"] = 2
    df.loc["WEST VIRGINIA", "Voter ID Law"] = 3
    df.loc["WISCONSIN", "Voter ID Law"] = 5
    df.loc["WYOMING", "Voter ID Law"] = 4

    # Quick clean up
    df = df.reset_index()
    df["inputstate"] = df["inputstate"].astype(int)
    df["Voter ID Law"] = df["Voter ID Law"].astype(int)

    return df


if __name__ == "__main__":

    fips_df = load_fips_data()
    print(fips_df.head())
