from pathlib import Path

from capstone.data_cleaning import load_dataframe, load_fips_data, load_voter_id_effect, merge_fips_ncsl
from capstone.helper_functions import load_config

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
