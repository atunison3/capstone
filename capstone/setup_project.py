import shutil
import pandas as pd
import requests
from io import StringIO
from pandas import DataFrame
from pathlib import Path
from typing import Optional

OUTPUT_DIR = Path(__file__).resolve().parent / ".data"


def get_user_downloads_folder() -> Path:
    """Return the platform-standard Downloads folder for the current user."""
    return Path.home() / "Downloads"


def create_data_directory(output_dir: Path = OUTPUT_DIR) -> None:
    """Creates the data folder"""

    output_dir.mkdir(parents=True, exist_ok=True)


def download_ces_data(
    output_dir: Path = OUTPUT_DIR,
    filename: str = "CCES24_Common_OUTPUT_vv_topost_final.csv",
) -> DataFrame:
    """
    Guide the user through a manual download of the CES file (required because
    automated access is blocked by Harvard Dataverse WAF protections).

    The function prints a clickable URL, instructs the user to save the file
    into their Downloads folder, waits for confirmation, moves the file into
    output_dir, and returns it as a pandas DataFrame.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # File page for the 2024 Common Content CSV (fileId=12050325)
    # Alternative cumulative dataset (preferred for most analyses):
    # https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/II2DB6
    file_page_url = "https://dataverse.harvard.edu/file.xhtml" "?fileId=12050325&version=9.0"

    downloads_dir = get_user_downloads_folder()
    source_path = downloads_dir / filename
    destination_path = output_dir / "ces_data.csv"

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
    print(line(f"   {str(downloads_dir)}"))
    print(empty)
    print(line("4. After the download has finished completely, return here."))
    print(empty)
    print(bottom)
    print()

    input(f"{margin}Press Enter once the file has finished downloading... ")

    # Allow a few common filename variations
    candidates = [
        source_path,
        downloads_dir / "CCES24_Common_OUTPUT_vv_topost_final.csv",
        downloads_dir / "ces_data.csv",
    ]

    found: Optional[Path] = None
    for candidate in candidates:
        if candidate.is_file() and candidate.stat().st_size > 0:
            found = candidate
            break

    if found is None:
        raise FileNotFoundError(
            f"Could not locate the downloaded file in {downloads_dir}.\n"
            f"Expected one of: {[str(c.name) for c in candidates]}\n"
            "Please verify the download completed and try again."
        )

    print(f"\nFound: {found}")
    print(f"Moving to: {destination_path}")

    if destination_path.exists():
        destination_path.unlink()

    shutil.move(str(found), str(destination_path))
    print("File moved successfully.")

    print("Loading into DataFrame (this may take a moment for large files)...")
    df = pd.read_csv(destination_path)
    print(f"Loaded shape: {df.shape}")
    return df


def download_state_data(output_dir: Path = OUTPUT_DIR) -> DataFrame:
    """Downloads FIPS data, saves it as CSV, and returns a DataFrame."""

    # Verify the output directory exists
    create_data_directory(output_dir)

    url = "https://www2.census.gov/geo/docs/reference/state.txt"
    output_path = output_dir / "fips.csv"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    dataframe = pd.read_csv(StringIO(response.text), sep="|")
    dataframe.to_csv(output_path, index=False)

    return dataframe


def install_ncsl_classification(
    output_dir: Path = OUTPUT_DIR,
    filename: str = "ncsl_voter_id_classification.csv",
) -> Path:
    """
    Create a DataFrame of state-level NCSL voter ID classifications
    (prose form) and save it as a CSV.

    Returns the path to the written file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

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
            "Non-Strict, Photo ID",  # Alabama = 3
            "Non-Strict, Non-Photo ID",  # Alaska = 2
            "Strict, Non-Photo ID",  # Arizona = 4
            "Strict, Photo ID",  # Arkansas = 5
            "No Document Required to Vote",  # California = 1
            "Non-Strict, Non-Photo ID",  # Colorado = 2
            "Non-Strict, Non-Photo ID",  # Connecticut = 2
            "Non-Strict, Non-Photo ID",  # Delaware = 2
            "No Document Required to Vote",  # District of Columbia = 0 → mapped to 1-style label
            "Non-Strict, Photo ID",  # Florida = 3
            "Strict, Photo ID",  # Georgia = 5
            "No Document Required to Vote",  # Hawaii = 1
            "Non-Strict, Photo ID",  # Idaho = 3
            "No Document Required to Vote",  # Illinois = 1
            "Strict, Photo ID",  # Indiana = 5
            "Non-Strict, Non-Photo ID",  # Iowa = 2
            "Strict, Photo ID",  # Kansas = 5
            "Non-Strict, Photo ID",  # Kentucky = 3
            "Non-Strict, Photo ID",  # Louisiana = 3
            "No Document Required to Vote",  # Maine = 1
            "No Document Required to Vote",  # Maryland = 1
            "No Document Required to Vote",  # Massachusetts = 1
            "Non-Strict, Photo ID",  # Michigan = 3
            "No Document Required to Vote",  # Minnesota = 1
            "Strict, Photo ID",  # Mississippi = 5
            "Non-Strict, Photo ID",  # Missouri = 3
            "Non-Strict, Photo ID",  # Montana = 3
            "Non-Strict, Photo ID",  # Nebraska = 3
            "No Document Required to Vote",  # Nevada = 1
            "Strict, Photo ID",  # New Hampshire = 5
            "No Document Required to Vote",  # New Jersey = 1
            "No Document Required to Vote",  # New Mexico = 1
            "No Document Required to Vote",  # New York = 1
            "Strict, Photo ID",  # North Carolina = 5
            "Non-Strict, Photo ID",  # North Dakota = 3
            "Strict, Photo ID",  # Ohio = 5
            "Non-Strict, Non-Photo ID",  # Oklahoma = 2
            "No Document Required to Vote",  # Oregon = 1
            "No Document Required to Vote",  # Pennsylvania = 1
            "Non-Strict, Photo ID",  # Rhode Island = 3
            "Non-Strict, Photo ID",  # South Carolina = 3
            "Non-Strict, Photo ID",  # South Dakota = 3
            "Strict, Photo ID",  # Tennessee = 5
            "Non-Strict, Photo ID",  # Texas = 3
            "Non-Strict, Non-Photo ID",  # Utah = 2
            "No Document Required to Vote",  # Vermont = 1
            "Non-Strict, Non-Photo ID",  # Virginia = 2
            "Non-Strict, Non-Photo ID",  # Washington = 2
            "Non-Strict, Photo ID",  # West Virginia = 3
            "Strict, Photo ID",  # Wisconsin = 5
            "Strict, Non-Photo ID",  # Wyoming = 4
        ],
    }

    df = pd.DataFrame(data)

    output_path = output_dir / filename
    df.to_csv(output_path, index=False)

    return output_path


def main(output_dir: Path = OUTPUT_DIR):
    """Creates data directory and downloads data to it."""
