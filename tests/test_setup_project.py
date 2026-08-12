import pandas as pd
import tempfile
import unittest
from pandas import DataFrame
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch


from capstone.setup_project import (
    create_data_directory,
    download_state_data,
    download_ces_data,
    get_user_downloads_folder,
    install_ncsl_classification,
)


class TestCreateDataDirectory(unittest.TestCase):
    def test_create_data_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / ".data"

            create_data_directory(output_dir)

            self.assertTrue(output_dir.exists())
            self.assertTrue(output_dir.is_dir())

    def test_create_data_directory_when_directory_already_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / ".data"
            output_dir.mkdir()

            create_data_directory(output_dir)

            self.assertTrue(output_dir.exists())
            self.assertTrue(output_dir.is_dir())


class TestDownloadStateData(unittest.TestCase):
    @patch("capstone.setup_project.requests.get")
    def test_download_state_data(self, mock_get: Mock) -> None:
        response = Mock()
        response.text = (
            "STATE|STUSAB|STATE_NAME|STATENS\n"
            "1|AL|Alabama|1779775\n"
            "2|AK|Alaska|1785533\n"
            "4|AZ|Arizona|1779777\n"
            "5|AR|Arkansas|68085\n"
            "6|CA|California|1779778\n"
        )
        mock_get.return_value = response

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            dataframe = download_state_data(output_dir)

            self.assertIsInstance(dataframe, pd.DataFrame)
            self.assertEqual(len(dataframe), 5)
            self.assertEqual(
                list(dataframe.columns),
                ["STATE", "STUSAB", "STATE_NAME", "STATENS"],
            )

            self.assertEqual(dataframe.iloc[0]["STATE"], 1)
            self.assertEqual(dataframe.iloc[0]["STUSAB"], "AL")
            self.assertEqual(dataframe.iloc[0]["STATE_NAME"], "Alabama")
            self.assertEqual(dataframe.iloc[0]["STATENS"], 1779775)

            output_path = output_dir / "fips.csv"

            self.assertTrue(output_path.exists())

            saved_dataframe = pd.read_csv(output_path)
            pd.testing.assert_frame_equal(dataframe, saved_dataframe)

            mock_get.assert_called_once_with(
                "https://www2.census.gov/geo/docs/reference/state.txt",
                timeout=60,
            )
            response.raise_for_status.assert_called_once()


class TestDownloadCesDataManual(unittest.TestCase):
    """Unit tests for download_ces_data."""

    def setUp(self) -> None:
        self.output_dir = Path("/tmp/test_ces_data")  # nosec: B108
        self.filename = "CCES24_Common_OUTPUT_vv_topost_final.csv"
        self.downloads_dir = Path("/tmp/fake_downloads")  # nosec: B108
        self.source_path = self.downloads_dir / self.filename
        self.destination_path = self.output_dir / "ces_data.csv"

        # Sample DataFrame that pd.read_csv will return
        self.sample_df = pd.DataFrame({"caseid": [1, 2, 3], "year": [2024, 2024, 2024]})

    @patch("capstone.setup_project.pd.read_csv")
    @patch("capstone.setup_project.shutil.move")
    @patch("capstone.setup_project.input", return_value="")
    @patch("capstone.setup_project.get_user_downloads_folder")
    @patch("capstone.setup_project.Path")
    def test_successful_download_and_move(
        self,
        mock_path_cls: MagicMock,
        mock_get_downloads: MagicMock,
        mock_input: MagicMock,
        mock_move: MagicMock,
        mock_read_csv: MagicMock,
    ) -> None:
        """Happy path: file is found in Downloads, moved, and loaded."""

        # Configure get_user_downloads_folder
        mock_get_downloads.return_value = self.downloads_dir

        # Configure Path behaviour for the output directory and source file
        mock_output_dir = MagicMock(spec=Path)
        mock_output_dir.mkdir = MagicMock()
        mock_destination = MagicMock(spec=Path)
        mock_destination.exists.return_value = False

        mock_source = MagicMock(spec=Path)
        mock_source.is_file.return_value = True
        mock_source.stat.return_value = MagicMock(st_size=1_000_000)

        # When Path is called with different arguments
        def path_side_effect(arg=None, *args, **kwargs):
            if arg == self.output_dir or str(arg).endswith(".data"):
                return mock_output_dir
            if "Downloads" in str(arg) or arg == self.downloads_dir:
                return self.downloads_dir
            return MagicMock(spec=Path)

        # Simpler approach: patch the specific objects the function uses
        with patch.object(Path, "home", return_value=Path("/tmp")):  # nosec: B108
            # Re-patch the key methods inside the function under test
            with patch("capstone.setup_project.Path") as mock_path:
                # We will control the objects returned by Path(...)
                mock_out = MagicMock()
                mock_out.mkdir = MagicMock()
                mock_dest = MagicMock()
                mock_dest.exists.return_value = False
                mock_out.__truediv__ = MagicMock(return_value=mock_dest)

                mock_dl = MagicMock()
                mock_src = MagicMock()
                mock_src.is_file.return_value = True
                mock_src.stat.return_value = MagicMock(st_size=500_000)
                mock_dl.__truediv__ = MagicMock(return_value=mock_src)

                # Path(output_dir) → mock_out
                # get_user_downloads_folder already patched to return mock_dl
                mock_path.side_effect = lambda p=None, *a, **k: mock_out

                mock_get_downloads.return_value = mock_dl
                mock_read_csv.return_value = self.sample_df

                result = download_ces_data(
                    output_dir=self.output_dir,
                    filename=self.filename,
                )

        # Assertions
        mock_input.assert_called_once()
        mock_move.assert_called_once()
        mock_read_csv.assert_called_once()
        self.assertIsInstance(result, DataFrame)
        self.assertEqual(len(result), 3)
        self.assertListEqual(list(result.columns), ["caseid", "year"])

    @patch("capstone.setup_project.input", return_value="")
    @patch("capstone.setup_project.get_user_downloads_folder")
    def test_file_not_found_raises(
        self,
        mock_get_downloads: MagicMock,
        mock_input: MagicMock,
    ) -> None:
        """When no candidate file exists, FileNotFoundError is raised."""

        mock_dl = MagicMock()
        # Every candidate returns is_file() == False
        mock_src = MagicMock()
        mock_src.is_file.return_value = False
        mock_dl.__truediv__ = MagicMock(return_value=mock_src)
        mock_get_downloads.return_value = mock_dl

        with self.assertRaises(FileNotFoundError) as ctx:
            download_ces_data(
                output_dir=self.output_dir,
                filename=self.filename,
            )

        self.assertIn("Could not locate the downloaded file", str(ctx.exception))
        mock_input.assert_called_once()

    def test_get_user_downloads_folder(self) -> None:
        """get_user_downloads_folder returns a Path under the home directory."""
        result = get_user_downloads_folder()
        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, "Downloads")
        self.assertTrue(str(result).startswith(str(Path.home())))


class TestInstallNcslClassification(unittest.TestCase):
    """Unit tests for install_ncsl_classification."""

    def test_creates_csv_with_expected_structure(self) -> None:
        """Function writes a CSV containing the correct columns and row count."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            result_path = install_ncsl_classification(
                output_dir=output_dir,
                filename="ncsl_test.csv",
            )

            # File was created at the expected location
            self.assertTrue(result_path.is_file())
            self.assertEqual(result_path, output_dir / "ncsl_test.csv")

            # Load and inspect contents
            df = pd.read_csv(result_path)

            self.assertListEqual(
                list(df.columns),
                ["State Name", "NCSL Classification"],
            )
            self.assertEqual(len(df), 51)  # 50 states + District of Columbia
            self.assertFalse(df.isnull().any().any())


def test_known_classifications(self) -> None:
    """Spot-check a few states against the hard-coded values."""
    with tempfile.TemporaryDirectory() as tmp:
        result_path = install_ncsl_classification(output_dir=Path(tmp))
        df = pd.read_csv(result_path).set_index("State Name")

        expected = {
            "California": "No Document Required to Vote",
            "Washington": "Non-Strict, Non-Photo ID",
            "Idaho": "Non-Strict, Photo ID",
            "Wyoming": "Strict, Non-Photo ID",
            "Kansas": "Strict, Photo ID",
            "Alabama": "Non-Strict, Photo ID",
            "Georgia": "Strict, Photo ID",
            "New York": "No Document Required to Vote",
        }

        for state, classification in expected.items():
            self.assertEqual(
                df.loc[state, "NCSL Classification"],
                classification,
                msg=f"Mismatch for {state}",
            )


def test_default_filename_and_directory_creation(self) -> None:
    """Default filename is used and missing directories are created."""
    with tempfile.TemporaryDirectory() as tmp:
        nested = Path(tmp) / "subdir" / "data"
        result_path = install_ncsl_classification(output_dir=nested)

        self.assertTrue(nested.is_dir())
        self.assertEqual(result_path.name, "ncsl_voter_id_classification.csv")
        self.assertTrue(result_path.is_file())


if __name__ == "__main__":
    unittest.main()
