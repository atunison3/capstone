import pandas as pd
import warnings
from pandas import DataFrame
from pathlib import Path
from typing import Any

from capstone.helper_functions import load_model_config, setup_logger

logger = setup_logger()


DATA_PATH = Path(".data")


def load_dataframe(data_path: Path = DATA_PATH) -> DataFrame:
    """Loads the CES data"""

    # Simply read the dataframe into a csv
    csv_path = data_path / "ces_data.csv"
    df = pd.read_csv(csv_path)

    logger.info("🟢 Successfully loaded the CES data.")

    return df


def load_fips_data(data_path: Path = DATA_PATH) -> DataFrame:
    """Loads the FIPS data"""

    # Read in csv
    csv_path = data_path / "fips.csv"
    df = pd.read_csv(csv_path)

    df = df.astype(
        {
            "STATE": "int64",
            "STUSAB": "string",
            "STATE_NAME": "string",
            "STATENS": "int64",
        }
    )

    df.rename(
        columns={
            "STATE": "State FIPS Code",
            "STATE_NAME": "State Name",
            "STUSAB": "State Code",
        },
        inplace=True,
    )

    logger.info("🟢 Successfully loaded the FIPS data.")

    return df


def load_voter_id_effect(data_path: Path) -> DataFrame:
    """Loads the NCSL data"""

    df = pd.read_csv(data_path / "ncsl_voter_id_classification.csv")
    logger.info("🟢 Successfully loaded the NCSL data.")

    return df


def rename_columns(df: DataFrame, column_map: dict[str, str]) -> DataFrame:
    """Renames dataframe columns"""

    df = df.rename(columns=column_map)

    return df


def merge_fips_ncsl(fips_df: DataFrame, ncsl_df: DataFrame) -> DataFrame:
    """Merges the FIPS and NCSL data"""

    merged_df = fips_df.merge(ncsl_df, on="State Name")

    # Drop unnecessary columns
    merged_df = merged_df.drop(columns=["STATENS"])

    return merged_df[["State Name", "State Code", "NCSL Classification", "State FIPS Code"]]


def clean_ces_data(df: DataFrame, config: dict[Any, Any]) -> DataFrame:
    """Clean the CES Data"""

    logger.info("🟢 Beginning cleaning of CES data")

    # Rename columns for human readability
    df = df.rename(columns=config["demographic_columns"])
    df = df.rename(columns=config["voter_outreach_columns"])
    df = df.rename(columns=config["state_column"])

    # Drop na
    df = df.dropna(subset=["TS_voterstatus"])

    # Determine who voted
    # 7 is did not vote (1 = Yes [voted] and 0 = No [did not vote])
    df["Voted"] = (df["TS_g2024"] != 7).astype(int)
    df["Age"] = 2024 - df["Birth Year"]

    # Map the columns
    for column_name, map_name in config["maps"].items():
        df[column_name] = df[column_name].astype(str).fillna("nan").replace(config[map_name])
        logger.debug(f"🟢 Successfully mapped {column_name}")
    df = df[config["full_columns"]]

    return df


def merge_ces_fips(ces_df: DataFrame, merged_fips_nscl: DataFrame) -> DataFrame:
    """Merges the CES on the"""

    return ces_df.merge(merged_fips_nscl, on="State FIPS Code")


def load_full_dataframe(config: dict[Any, Any]) -> DataFrame:
    """Loads the full dataframe and cleans"""

    data_path = Path(config["data_path"])

    # Loads the CES data and cleans it
    df = load_dataframe(data_path)
    df = clean_ces_data(df, config)

    # Loads the fips data
    fips_df = load_fips_data(data_path)

    # Generates the NCSL dataframe
    ncsl_df = load_voter_id_effect(data_path)

    # Merges the NCSL data onto the FIPS data
    merged_fips_ncsl_df = merge_fips_ncsl(fips_df, ncsl_df)

    # Merges the CES and FIPS data
    final_df = merge_ces_fips(df, merged_fips_ncsl_df)

    return final_df.dropna(subset=config["features"])


def main() -> DataFrame:

    # Get the data path
    model_config = load_model_config()

    df = load_full_dataframe(model_config)

    return df


if __name__ == "__main__":

    warnings.filterwarnings("ignore")
    logger.info("🟡 Ignored warnings in data_cleaning.py")

    df = main()
    print(df.head())
    print(df.dtypes)
