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

    # Data cleaning
    df.rename(
        columns={
            "STATE": "State FIPS Code",
            "STATE_NAME": "State Name",
            "STUSAB": "State Code",
        },
        inplace=True,
    )

    # Save the dataframe so we don't need to request it next time
    df.to_csv(fips_path, index=False)

    return df


def load_voter_id_effect(data_path: Path) -> DataFrame:
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

    df = load_fips_data(data_path)
    df = df.set_index("State Name")

    # Fill in states from image
    df.loc["Alabama", "NCSL Classification"] = 3
    df.loc["Alaska", "NCSL Classification"] = 2
    df.loc["Arizona", "NCSL Classification"] = 4
    df.loc["Arkansas", "NCSL Classification"] = 5
    df.loc["California", "NCSL Classification"] = 1
    df.loc["Colorado", "NCSL Classification"] = 2
    df.loc["Connecticut", "NCSL Classification"] = 2
    df.loc["Delaware", "NCSL Classification"] = 2
    df.loc["District of Columbia", "NCSL Classification"] = 0
    df.loc["Florida", "NCSL Classification"] = 3
    df.loc["Georgia", "NCSL Classification"] = 5
    df.loc["Hawaii", "NCSL Classification"] = 1
    df.loc["Idaho", "NCSL Classification"] = 3
    df.loc["Illinois", "NCSL Classification"] = 1
    df.loc["Indiana", "NCSL Classification"] = 5
    df.loc["Iowa", "NCSL Classification"] = 2
    df.loc["Kansas", "NCSL Classification"] = 5
    df.loc["Kentucky", "NCSL Classification"] = 3
    df.loc["Louisiana", "NCSL Classification"] = 3
    df.loc["Maine", "NCSL Classification"] = 1
    df.loc["Maryland", "NCSL Classification"] = 1
    df.loc["Massachusetts", "NCSL Classification"] = 1
    df.loc["Michigan", "NCSL Classification"] = 3
    df.loc["Minnesota", "NCSL Classification"] = 1
    df.loc["Mississippi", "NCSL Classification"] = 5
    df.loc["Missouri", "NCSL Classification"] = 3
    df.loc["Montana", "NCSL Classification"] = 3
    df.loc["Nebraska", "NCSL Classification"] = 3
    df.loc["Nevada", "NCSL Classification"] = 1
    df.loc["New Hampshire", "NCSL Classification"] = 5
    df.loc["New Jersey", "NCSL Classification"] = 1
    df.loc["New Mexico", "NCSL Classification"] = 1
    df.loc["New York", "NCSL Classification"] = 1
    df.loc["North Carolina", "NCSL Classification"] = 5
    df.loc["North Dakota", "NCSL Classification"] = 3
    df.loc["Ohio", "NCSL Classification"] = 5
    df.loc["Oklahoma", "NCSL Classification"] = 2
    df.loc["Oregon", "NCSL Classification"] = 1
    df.loc["Pennsylvania", "NCSL Classification"] = 1
    df.loc["Rhode Island", "NCSL Classification"] = 3
    df.loc["South Carolina", "NCSL Classification"] = 3
    df.loc["South Dakota", "NCSL Classification"] = 3
    df.loc["Tennessee", "NCSL Classification"] = 5
    df.loc["Texas", "NCSL Classification"] = 3
    df.loc["Utah", "NCSL Classification"] = 2
    df.loc["Vermont", "NCSL Classification"] = 1
    df.loc["Virginia", "NCSL Classification"] = 2
    df.loc["Washington", "NCSL Classification"] = 2
    df.loc["West Virginia", "NCSL Classification"] = 3
    df.loc["Wisconsin", "NCSL Classification"] = 5
    df.loc["Wyoming", "NCSL Classification"] = 4

    # Quick clean up
    df = df.dropna(subset=["NCSL Classification"])  # Drops territories we aren't considering
    df = df.reset_index()
    df["State Name"] = df["State Name"].astype(str)
    df["NCSL Classification"] = df["NCSL Classification"].astype(int).astype(str)

    classification_map = {
        "5": "Strict Photo ID",
        "4": "Strict Non-Photo ID",
        "3": "Non-Strict Photo ID",
        "2": "Non-Strict, Non-Photo ID",
        "1": "No Document Required to Vote",
    }
    df["NCSL Classification"] = df["NCSL Classification"].astype("string").map(classification_map)

    return df[["State Name", "NCSL Classification"]]


def rename_columns(df: DataFrame, column_map: dict[str, str]) -> DataFrame:
    """Renames dataframe columns"""

    df = df.rename(columns=column_map)

    return df


def merge_fips_ncsl(fips_df: DataFrame, ncsl_df: DataFrame) -> DataFrame:
    """Merges the two"""

    merged_df = fips_df.merge(ncsl_df, on="State Name")

    # Drop unnecessary columns
    merged_df = merged_df.drop(columns=["STATENS"])

    return merged_df[["State Name", "State Code", "NCSL Classification", "State FIPS Code"]]


if __name__ == "__main__":

    # Get the data path
    config = load_config()
    data_path = Path(config["data_path"]) / "dev"

    # Load the dataframe
    df = load_dataframe(data_path)
    print(df.head())

    fips_df = load_fips_data(data_path)
    print(fips_df.head())

    ncsl_df = load_voter_id_effect(data_path)
    print(ncsl_df.head())

    print(merge_fips_ncsl(fips_df, ncsl_df))
