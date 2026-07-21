import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import requests

from capstone.data_cleaning import load_dataframe, load_fips_data


class TestLoadDataFrame(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_directory.name)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_loads_dataframe_from_data_csv(self) -> None:
        csv_path = self.temp_path / "data.csv"

        expected = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "state": ["TX", "CA", "NY"],
            }
        )
        expected.to_csv(csv_path, index=False)

        result = load_dataframe(self.temp_path)

        pd.testing.assert_frame_equal(result, expected)

    def test_missing_data_csv_raises_file_not_found_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_dataframe(self.temp_path)

    def test_empty_csv_raises_empty_data_error(self) -> None:
        csv_path = self.temp_path / "data.csv"
        csv_path.write_text("", encoding="utf-8")

        with self.assertRaises(pd.errors.EmptyDataError):
            load_dataframe(self.temp_path)

    def test_invalid_csv_still_returns_dataframe(self) -> None:
        csv_path = self.temp_path / "data.csv"
        csv_path.write_text(
            "id,state\n" '1,"Texas\n' "2,California\n",
            encoding="utf-8",
        )

        with self.assertRaises(pd.errors.ParserError):
            load_dataframe(self.temp_path)

    def test_preserves_csv_columns(self) -> None:
        csv_path = self.temp_path / "data.csv"
        csv_path.write_text(
            "inputstate,voted,weight\n" "01,1,0.75\n" "48,0,1.25\n",
            encoding="utf-8",
        )

        result = load_dataframe(self.temp_path)

        self.assertEqual(
            result.columns.tolist(),
            ["inputstate", "voted", "weight"],
        )
        self.assertEqual(len(result), 2)


class TestLoadFipsData(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_directory.name)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    # def test_loads_existing_fips_csv_without_request(self) -> None:
    #     expected = pd.DataFrame(
    #         {
    #             "State FIPS Code": pd.Series(["01", "02"], dtype="string"),
    #             "State Name": ["Alabama", "Alaska"],
    #         }
    #     )
    #     expected.to_csv(self.data_path / "fips.csv", index=False)

    #     with patch("capstone.data_cleaning.requests.get") as mock_get:
    #         result = load_fips_data(self.data_path)

    #     mock_get.assert_not_called()
    #     pd.testing.assert_frame_equal(result, expected)

    @patch("capstone.data_cleaning.requests.get")
    def test_downloads_saves_and_returns_fips_data(
        self,
        mock_get: Mock,
    ) -> None:
        response_text = (
            "STATE|STUSAB|STATE_NAME|STATENS\n"
            "01|AL|Alabama|01779775\n"
            "02|AK|Alaska|01785533\n"
            "04|AZ|Arizona|01779777\n"
        )

        mock_response = Mock()
        mock_response.text = response_text
        mock_get.return_value = mock_response

        result = load_fips_data(self.data_path)

        expected = pd.DataFrame(
            {
                "State FIPS Code": pd.Series(["01", "02", "04"], dtype="string"),
                "State Code": pd.Series(["AL", "AK", "AZ"], dtype="string"),
                "State Name": pd.Series(
                    ["Alabama", "Alaska", "Arizona"],
                    dtype="string",
                ),
                "STATENS": pd.Series(
                    ["01779775", "01785533", "01779777"],
                    dtype="string",
                ),
            }
        )

        mock_get.assert_called_once_with(
            "https://www2.census.gov/geo/docs/reference/state.txt",
            timeout=30,
        )
        mock_response.raise_for_status.assert_called_once_with()

        pd.testing.assert_frame_equal(result, expected)

        saved_path = self.data_path / "fips.csv"
        self.assertTrue(saved_path.exists())

        saved = pd.read_csv(
            saved_path,
            dtype={
                "State FIPS Code": "string",
                "State Code": "string",
                "State Name": "string",
                "STATENS": "string",
            },
        )
        pd.testing.assert_frame_equal(saved, expected)

    @patch("capstone.data_cleaning.requests.get")
    def test_preserves_leading_zeros(
        self,
        mock_get: Mock,
    ) -> None:
        mock_response = Mock()
        mock_response.text = "STATE|STUSAB|STATE_NAME|STATENS\n" "01|AL|Alabama|01779775\n"
        mock_get.return_value = mock_response

        result = load_fips_data(self.data_path)

        self.assertEqual(result.loc[0, "State FIPS Code"], "01")
        self.assertEqual(result.loc[0, "STATENS"], "01779775")

    @patch("capstone.data_cleaning.requests.get")
    def test_http_error_is_propagated(
        self,
        mock_get: Mock,
    ) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
        mock_get.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            load_fips_data(self.data_path)

        self.assertFalse((self.data_path / "fips.csv").exists())

    @patch("capstone.data_cleaning.requests.get")
    def test_request_exception_is_propagated(
        self,
        mock_get: Mock,
    ) -> None:
        mock_get.side_effect = requests.ConnectionError("Unable to connect")

        with self.assertRaises(requests.ConnectionError):
            load_fips_data(self.data_path)

        self.assertFalse((self.data_path / "fips.csv").exists())

    def test_file_path_raises_not_a_directory_error(self) -> None:
        file_path = self.data_path / "not-a-directory"
        file_path.write_text("content", encoding="utf-8")

        with self.assertRaisesRegex(
            NotADirectoryError,
            "Data path is not a directory",
        ):
            load_fips_data(file_path)

    def test_missing_data_path_raises_file_not_found_error(self) -> None:
        missing_path = self.data_path / "missing-directory"

        with self.assertRaises(FileNotFoundError):
            load_fips_data(missing_path)


if __name__ == "__main__":
    unittest.main()
