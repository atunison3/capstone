import shutil
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from capstone.helper_functions import setup_logger


OUTPUT_DIR = Path(".data")

logger = setup_logger()


def get_user_downloads_folder() -> Path:
    """Return the platform-standard Downloads folder for the current user."""

    downloads_dir = Path.home() / "Downloads"
    logger.debug("🟢 User Downloads directory resolved to: %s", downloads_dir)

    return downloads_dir


def create_data_directory(output_dir: Path = OUTPUT_DIR) -> None:
    """Creates the data folder."""

    logger.debug("🟢 Verifying data directory exists: %s", output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception("🔴 Failed to create data directory: %s", output_dir)
        raise

    logger.debug("🟢 Data directory is available: %s", output_dir)


def download_ces_data(
    output_dir: Path = OUTPUT_DIR,
    filename: str = "CCES24_Common_OUTPUT_vv_topost_final.csv",
) -> None:
    """
    Guide the user through a manual download of the CES file.

    Automated access is blocked by Harvard Dataverse WAF protections. The function
    instructs the user to download the file, locates it in the Downloads folder,
    moves it into the data directory, and returns it as a pandas DataFrame.
    """

    logger.info("🟢 Starting CES data installation.")

    if (output_dir / "ces_data.csv").exists():
        logger.info("🟢 CES Data exists. Exiting download of ces data.")
        return None

    output_dir = Path(output_dir)
    create_data_directory(output_dir)

    file_page_url = "https://dataverse.harvard.edu/file.xhtml?fileId=12050325&version=9.0"

    downloads_dir = get_user_downloads_folder()
    source_path = downloads_dir / filename
    destination_path = output_dir / "ces_data.csv"

    logger.debug("🟡 Expected CES download filename: %s", filename)
    logger.debug("🟡 CES download directory: %s", downloads_dir)
    logger.debug("🟡 CES destination path: %s", destination_path)

    margin = "   "
    width = 80
    top = f"{margin}╭{'─' * width}╮"
    header_sep = f"{margin}├{'─' * width}┤"
    bottom = f"{margin}╰{'─' * width}╯"
    empty = f"{margin}│{' ' * width}│"

    def line(text: str) -> str:
        return f"{margin}│ {text:<{width - 1}}│"

    print()
    print(top)
    print(line("MANUAL DOWNLOAD REQUIRED"))
    print(header_sep)
    print(empty)
    print(line("Automated download from Harvard Dataverse is currently blocked."))
    print(line("Please complete the following steps:"))
    print(empty)
    print(line("1. Open the following URL in your web browser (clickable):"))
    print(empty)
    print(line(f"   {file_page_url}"))
    print(empty)
    print(line("2. Click the blue 'Access File' button (or the download option)."))
    print(line(f"3. Save the file as '{filename}'"))
    print(line("   into your Downloads folder:"))
    print(line(f"   {downloads_dir}"))
    print(empty)
    print(line("4. After the download has finished completely, return here."))
    print(empty)
    print(bottom)
    print()

    logger.info("🟡 Waiting for manual CES download to complete.")

    input(f"{margin}Press Enter once the file has finished downloading... ")

    candidates = [
        source_path,
        downloads_dir / "CCES24_Common_OUTPUT_vv_topost_final.csv",
        downloads_dir / "ces_data.csv",
    ]

    logger.debug("🟢 Searching for downloaded CES file.")

    found: Optional[Path] = None

    for candidate in candidates:
        logger.debug("🟡 Checking candidate file: %s", candidate)

        if candidate.is_file() and candidate.stat().st_size > 0:
            found = candidate
            logger.info("🟢 Found CES data file: %s", found)
            break

    if found is None:
        candidate_names = [candidate.name for candidate in candidates]

        logger.error(
            "🔴 Could not locate CES data in %s. Expected one of: %s",
            downloads_dir,
            candidate_names,
        )

        raise FileNotFoundError(
            f"Could not locate the downloaded file in {downloads_dir}.\n"
            f"Expected one of: {candidate_names}\n"
            "Please verify the download completed and try again."
        )

    if destination_path.exists():
        logger.warning("🟡 Existing CES data file will be replaced: %s", destination_path)

        try:
            destination_path.unlink()
        except OSError:
            logger.exception("🔴 Failed to remove existing CES data file: %s", destination_path)
            raise

    logger.info("🟢 Moving CES data from %s to %s", found, destination_path)

    try:
        shutil.move(str(found), str(destination_path))
    except OSError:
        logger.exception("🔴 Failed to move CES data to: %s", destination_path)
        raise

    logger.info("🟢 CES data moved successfully.")

    logger.info("🟢 Loading CES data into a DataFrame.")

    try:
        dataframe = pd.read_csv(destination_path)
    except Exception:
        logger.exception("🔴 Failed to load CES data from: %s", destination_path)
        raise

    logger.info(
        "🟢 CES DataFrame loaded successfully with %d rows and %d columns.",
        dataframe.shape[0],
        dataframe.shape[1],
    )

    logger.debug("🟡 Writing normalized CES data to: %s", destination_path)

    try:
        dataframe.to_csv(destination_path, index=False)
    except OSError:
        logger.exception("🔴 Failed to save CES DataFrame to: %s", destination_path)
        raise

    logger.info("🟢 CES data installation complete.")

    return None


def download_state_data(output_dir: Path = OUTPUT_DIR) -> None:
    """Downloads FIPS data, saves it as CSV, and returns a DataFrame."""

    logger.info("🟢 Starting Census FIPS data download.")

    # Check if data already exists
    if (output_dir / "fips.csv").exists():
        logger.info("🟢 State data exists. Exiting the download of state data.")
        return None

    create_data_directory(output_dir)

    url = "https://www2.census.gov/geo/docs/reference/state.txt"
    output_path = output_dir / "fips.csv"

    logger.debug("🟢 Requesting FIPS data from: %s", url)

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("🔴 Failed to download FIPS data from: %s", url)
        raise

    logger.info("🟢 FIPS data downloaded successfully.")

    try:
        dataframe = pd.read_csv(StringIO(response.text), sep="|")
    except Exception:
        logger.exception("🔴 Failed to parse FIPS data.")
        raise

    logger.info(
        "🟢 FIPS DataFrame created with %d rows and %d columns.",
        dataframe.shape[0],
        dataframe.shape[1],
    )

    try:
        dataframe.to_csv(output_path, index=False)
    except OSError:
        logger.exception("🔴 Failed to save FIPS data to: %s", output_path)
        raise

    logger.info("🟢 FIPS data saved to: %s", output_path)

    return None


def install_ncsl_classification(
    output_dir: Path = OUTPUT_DIR,
    filename: str = "ncsl_voter_id_classification.csv",
) -> None:
    """
    Create a DataFrame of state-level NCSL voter ID classifications and save it as a CSV.

    Returns the path to the written file.
    """

    logger.info("🟢 Installing NCSL voter ID classification data.")

    # Checkout if ncsl data exists
    if (output_dir / "ncsl_voter_id_classification.csv").exists():
        logger.info("🟢 NCSL Voter ID Classification data exists. Exiting install.")
        return None

    create_data_directory(output_dir)

    data = {
        "State Name": [
            "Alabama",
            "Alaska",
            "Arizona",
            "Arkansas",
            "California",
            "Colorado",
            "Connecticut",
            "Delaware",
            "District of Columbia",
            "Florida",
            "Georgia",
            "Hawaii",
            "Idaho",
            "Illinois",
            "Indiana",
            "Iowa",
            "Kansas",
            "Kentucky",
            "Louisiana",
            "Maine",
            "Maryland",
            "Massachusetts",
            "Michigan",
            "Minnesota",
            "Mississippi",
            "Missouri",
            "Montana",
            "Nebraska",
            "Nevada",
            "New Hampshire",
            "New Jersey",
            "New Mexico",
            "New York",
            "North Carolina",
            "North Dakota",
            "Ohio",
            "Oklahoma",
            "Oregon",
            "Pennsylvania",
            "Rhode Island",
            "South Carolina",
            "South Dakota",
            "Tennessee",
            "Texas",
            "Utah",
            "Vermont",
            "Virginia",
            "Washington",
            "West Virginia",
            "Wisconsin",
            "Wyoming",
        ],
        "NCSL Classification": [
            "Non-Strict, Photo ID",
            "Non-Strict, Non-Photo ID",
            "Strict, Non-Photo ID",
            "Strict, Photo ID",
            "No Document Required to Vote",
            "Non-Strict, Non-Photo ID",
            "Non-Strict, Non-Photo ID",
            "Non-Strict, Non-Photo ID",
            "No Document Required to Vote",
            "Non-Strict, Photo ID",
            "Strict, Photo ID",
            "No Document Required to Vote",
            "Non-Strict, Photo ID",
            "No Document Required to Vote",
            "Strict, Photo ID",
            "Non-Strict, Non-Photo ID",
            "Strict, Photo ID",
            "Non-Strict, Photo ID",
            "Non-Strict, Photo ID",
            "No Document Required to Vote",
            "No Document Required to Vote",
            "No Document Required to Vote",
            "Non-Strict, Photo ID",
            "No Document Required to Vote",
            "Strict, Photo ID",
            "Non-Strict, Photo ID",
            "Non-Strict, Photo ID",
            "Non-Strict, Photo ID",
            "No Document Required to Vote",
            "Strict, Photo ID",
            "No Document Required to Vote",
            "No Document Required to Vote",
            "No Document Required to Vote",
            "Strict, Photo ID",
            "Non-Strict, Photo ID",
            "Strict, Photo ID",
            "Non-Strict, Non-Photo ID",
            "No Document Required to Vote",
            "No Document Required to Vote",
            "Non-Strict, Photo ID",
            "Non-Strict, Photo ID",
            "Non-Strict, Photo ID",
            "Strict, Photo ID",
            "Non-Strict, Photo ID",
            "Non-Strict, Non-Photo ID",
            "No Document Required to Vote",
            "Non-Strict, Non-Photo ID",
            "Non-Strict, Non-Photo ID",
            "Non-Strict, Photo ID",
            "Strict, Photo ID",
            "Strict, Non-Photo ID",
        ],
    }

    logger.debug("🟢 Creating NCSL classification DataFrame.")

    dataframe = pd.DataFrame(data)

    logger.info(
        "🟢 NCSL DataFrame created with %d rows and %d columns.",
        dataframe.shape[0],
        dataframe.shape[1],
    )

    output_path = output_dir / filename

    try:
        dataframe.to_csv(output_path, index=False)
    except OSError:
        logger.exception("🔴 Failed to save NCSL classification data to: %s", output_path)
        raise

    logger.info("🟢 NCSL classification data saved to: %s", output_path)

    return None


def main(output_dir: Path = OUTPUT_DIR) -> None:
    """Creates the data directory and installs all required project data."""

    logger.info("🟢 Starting capstone project data setup.")

    try:
        create_data_directory(output_dir)

        logger.info("🟢 Installing CES data.")
        download_ces_data(output_dir)

        logger.info("🟢 Installing Census FIPS data.")
        download_state_data(output_dir)

        logger.info("🟢 Installing NCSL voter ID classification data.")
        install_ncsl_classification(output_dir)

    except Exception:
        logger.exception("🔴 Capstone project data setup failed.")
        raise

    logger.info("🟢 Capstone project data setup completed successfully.")


if __name__ == "__main__":
    main()
