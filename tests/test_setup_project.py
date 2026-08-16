"""Tests for capstone.setup_project."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from capstone import setup_project as sp


class TestGetUserDownloadsFolder(unittest.TestCase):
    def test_returns_home_downloads(self) -> None:
        with patch.object(Path, "home", return_value=Path("/Users/example")):
            result = sp.get_user_downloads_folder()

        self.assertEqual(result, Path("/Users/example") / "Downloads")


class TestCreateDataDirectory(unittest.TestCase):
    def test_creates_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "nested" / ".data"
            sp.create_data_directory(target)

            self.assertTrue(target.is_dir())

    def test_existing_directory_is_ok(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            sp.create_data_directory(target)
            sp.create_data_directory(target)
            self.assertTrue(target.is_dir())


class TestDownloadCesData(unittest.TestCase):
    def test_noop_when_ces_csv_already_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            (output_dir / "ces_data.csv").write_text("a\n1\n", encoding="utf-8")

            with patch.object(sp, "create_data_directory") as mock_create:
                with patch.object(sp, "input", side_effect=AssertionError("should not prompt")):
                    sp.download_ces_data(output_dir)

            mock_create.assert_not_called()

    def test_moves_downloaded_file_and_normalizes_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_dir = root / ".data"
            downloads = root / "Downloads"
            downloads.mkdir()
            output_dir.mkdir()

            source = downloads / "CCES24_Common_OUTPUT_vv_topost_final.csv"
            pd.DataFrame({"col": [1, 2]}).to_csv(source, index=False)

            with (
                patch.object(sp, "get_user_downloads_folder", return_value=downloads),
                patch.object(sp, "input", return_value=""),
            ):
                sp.download_ces_data(output_dir)

            dest = output_dir / "ces_data.csv"
            self.assertTrue(dest.exists())
            self.assertFalse(source.exists())
            loaded = pd.read_csv(dest)
            self.assertEqual(list(loaded["col"]), [1, 2])

    def test_missing_download_raises_file_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_dir = root / ".data"
            downloads = root / "Downloads"
            downloads.mkdir()

            with (
                patch.object(sp, "get_user_downloads_folder", return_value=downloads),
                patch.object(sp, "input", return_value=""),
            ):
                with self.assertRaises(FileNotFoundError) as ctx:
                    sp.download_ces_data(output_dir)

            self.assertIn("Could not locate the downloaded file", str(ctx.exception))


class TestDownloadStateData(unittest.TestCase):
    def test_noop_when_fips_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            (output_dir / "fips.csv").write_text("STATE|STUSAB\n26|MI\n", encoding="utf-8")

            with patch.object(sp.requests, "get") as mock_get:
                sp.download_state_data(output_dir)

            mock_get.assert_not_called()

    def test_downloads_parses_and_writes_fips_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            body = "STATE|STUSAB|STATE_NAME|STATENS\n26|MI|Michigan|1779780\n"

            mock_response = Mock()
            mock_response.text = body
            mock_response.raise_for_status = Mock()

            with patch.object(sp.requests, "get", return_value=mock_response) as mock_get:
                sp.download_state_data(output_dir)

            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            self.assertIn("census.gov", args[0])
            self.assertEqual(kwargs.get("timeout"), 60)

            path = output_dir / "fips.csv"
            self.assertTrue(path.exists())
            frame = pd.read_csv(path)
            self.assertEqual(frame.iloc[0]["STUSAB"], "MI")
            self.assertEqual(int(frame.iloc[0]["STATE"]), 26)

    def test_request_error_is_raised(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            with patch.object(
                sp.requests,
                "get",
                side_effect=sp.requests.RequestException("network down"),
            ):
                with self.assertRaises(sp.requests.RequestException):
                    sp.download_state_data(output_dir)


class TestInstallNcslClassification(unittest.TestCase):
    def test_noop_when_file_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            target = output_dir / "ncsl_voter_id_classification.csv"
            target.write_text("State Name,NCSL Classification\nMichigan,x\n", encoding="utf-8")

            sp.install_ncsl_classification(output_dir)
            # Unchanged single data row (+ header)
            self.assertEqual(len(target.read_text(encoding="utf-8").splitlines()), 2)

    def test_writes_fifty_one_jurisdictions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            sp.install_ncsl_classification(output_dir)

            path = output_dir / "ncsl_voter_id_classification.csv"
            self.assertTrue(path.exists())
            frame = pd.read_csv(path)
            self.assertEqual(len(frame), 51)
            self.assertListEqual(
                list(frame.columns),
                ["State Name", "NCSL Classification"],
            )
            self.assertIn("Michigan", set(frame["State Name"]))
            self.assertTrue(frame["NCSL Classification"].notna().all())


class TestSetupMain(unittest.TestCase):
    def test_main_runs_all_install_steps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            with (
                patch.object(sp, "create_data_directory") as mock_create,
                patch.object(sp, "download_ces_data") as mock_ces,
                patch.object(sp, "download_state_data") as mock_fips,
                patch.object(sp, "install_ncsl_classification") as mock_ncsl,
            ):
                sp.main(output_dir)

            mock_create.assert_called_once_with(output_dir)
            mock_ces.assert_called_once_with(output_dir)
            mock_fips.assert_called_once_with(output_dir)
            mock_ncsl.assert_called_once_with(output_dir)

    def test_main_reraises_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            with (
                patch.object(sp, "create_data_directory"),
                patch.object(sp, "download_ces_data", side_effect=RuntimeError("boom")),
            ):
                with self.assertRaises(RuntimeError):
                    sp.main(output_dir)


if __name__ == "__main__":
    unittest.main()
