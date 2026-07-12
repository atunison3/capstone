from pandas import DataFrame

import capstone.helper_functions as fun


def clean_ces_data(df: DataFrame) -> DataFrame:
    """Cleans the CES Data"""

    return df


def merge_voter_strictness(df: DataFrame, voter_id_strictness_df: DataFrame) -> DataFrame:
    """Merges the voter ID strictness data into the CES data"""

    return df.merge(voter_id_strictness_df, on="inputstate")[["caseid", "inputstate", "Voter ID Law"]]


if __name__ == "__main__":
    from pathlib import Path

    # Load the config
    config_path = Path("config.local.toml")
    config = fun.load_config(config_path)

    # Load the CES data
    data_path = Path(config["data_path"])
    df = fun.load_ces_data(data_path / "dev/data.csv")
    print(df.head())

    # Get the voter laws
    voter_laws_df = fun.load_voter_id_effect()
    print(voter_laws_df.head())

    print(merge_voter_strictness(df, voter_laws_df).head())
