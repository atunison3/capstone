"""Tests for capstone.data_cleaning."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from pandas import DataFrame

from capstone.data_cleaning import (
    clean_ces_data,
    load_dataframe,
    load_fips_data,
    load_full_dataframe,
    load_voter_id_effect,
    merge_ces_fips,
    merge_fips_ncsl,
    rename_columns,
)
from capstone.helper_functions import load_model_config


def _model_config() -> dict:
    """Config dict with lowercase keys matching load_model_config()."""
    return load_model_config()


def _raw_ces_frame() -> DataFrame:
    """Minimal raw CES-like frame using original column names."""
    return DataFrame(
        {
            "educ": [1, 5, 2, 6],
            "race": [1, 2, 1, 3],
            "hispanic": [2, 2, 2, 1],
            "gender4": [1, 2, 1, 2],
            "birthyr": [1990, 1985, 2000, 1970],
            "CC24_431b_1": [1.0, 2.0, np.nan, 1.0],
            "CC24_431b_2": [2.0, 1.0, 2.0, 2.0],
            "CC24_431b_3": [2.0, 2.0, 1.0, 2.0],
            "CC24_431b_4": [2.0, 2.0, 2.0, 1.0],
            "inputstate": [26, 6, 26, 48],
            "TS_voterstatus": ["active", "active", np.nan, "active"],
            "TS_g2024": [4, 7, 1, 2],
        }
    )


class TestRenameColumns(unittest.TestCase):
    def test_renames_matching_columns(self) -> None:
        df = DataFrame({"a": [1], "b": [2]})
        result = rename_columns(df, {"a": "A"})

        self.assertListEqual(list(result.columns), ["A", "b"])
        self.assertEqual(result.loc[0, "A"], 1)

    def test_does_not_mutate_original(self) -> None:
        df = DataFrame({"a": [1]})
        rename_columns(df, {"a": "A"})
        self.assertIn("a", df.columns)


class TestMergeFipsNcsl(unittest.TestCase):
    def test_merges_on_state_name_and_selects_columns(self) -> None:
        fips = DataFrame(
            {
                "State FIPS Code": [26, 6],
                "State Name": ["Michigan", "California"],
                "State Code": ["MI", "CA"],
                "STATENS": [1, 2],
            }
        )
        ncsl = DataFrame(
            {
                "State Name": ["Michigan", "California"],
                "NCSL Classification": ["Non-Strict, Photo ID", "No Document Required to Vote"],
            }
        )

        result = merge_fips_ncsl(fips, ncsl)

        self.assertListEqual(
            list(result.columns),
            ["State Name", "State Code", "NCSL Classification", "State FIPS Code"],
        )
        self.assertEqual(len(result), 2)
        self.assertNotIn("STATENS", result.columns)
        mi = result.loc[result["State Name"] == "Michigan"].iloc[0]
        self.assertEqual(mi["State Code"], "MI")
        self.assertEqual(mi["NCSL Classification"], "Non-Strict, Photo ID")

    def test_inner_join_drops_unmatched_states(self) -> None:
        fips = DataFrame(
            {
                "State FIPS Code": [26],
                "State Name": ["Michigan"],
                "State Code": ["MI"],
                "STATENS": [1],
            }
        )
        ncsl = DataFrame(
            {
                "State Name": ["Texas"],
                "NCSL Classification": ["Non-Strict, Photo ID"],
            }
        )

        result = merge_fips_ncsl(fips, ncsl)
        self.assertEqual(len(result), 0)


class TestMergeCesFips(unittest.TestCase):
    def test_merges_on_state_fips_code(self) -> None:
        ces = DataFrame({"State FIPS Code": [26, 6], "Voted": [1, 0]})
        state = DataFrame(
            {
                "State FIPS Code": [26],
                "State Name": ["Michigan"],
                "State Code": ["MI"],
                "NCSL Classification": ["Non-Strict, Photo ID"],
            }
        )

        result = merge_ces_fips(ces, state)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["State Name"], "Michigan")
        self.assertEqual(result.iloc[0]["Voted"], 1)


class TestCleanCesData(unittest.TestCase):
    def setUp(self) -> None:
        self.config = _model_config()
        self.raw = _raw_ces_frame()

    def test_drops_rows_missing_voter_status(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        # One of four rows has missing TS_voterstatus
        self.assertEqual(len(cleaned), 3)

    def test_voted_is_zero_when_ts_g2024_is_7(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        # birthyr 1985 row had TS_g2024 == 7
        no_vote = cleaned.loc[cleaned["Age"] == 2024 - 1985].iloc[0]
        self.assertEqual(int(no_vote["Voted"]), 0)

    def test_voted_is_one_for_other_vote_methods(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        voters = cleaned.loc[cleaned["Voted"] == 1]
        self.assertGreaterEqual(len(voters), 1)
        self.assertTrue((voters["Voted"] == 1).all())

    def test_age_is_2024_minus_birth_year(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        self.assertIn(34, set(cleaned["Age"].tolist()))  # 2024 - 1990

    def test_maps_education_codes_to_labels(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        self.assertIn("No HS degree", set(cleaned["Education"].astype(str)))
        self.assertIn("4 year college degree", set(cleaned["Education"].astype(str)))

    def test_maps_nan_outreach_to_no(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        # Row with nan in-person should become No after mapping
        self.assertTrue(set(cleaned["In person"].astype(str)).issubset({"Yes", "No"}))

    def test_retains_only_full_columns(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        self.assertListEqual(list(cleaned.columns), list(self.config["full_columns"]))

    def test_renames_state_and_outreach_columns(self) -> None:
        cleaned = clean_ces_data(self.raw.copy(), self.config)
        self.assertIn("State FIPS Code", cleaned.columns)
        self.assertIn("Phone call", cleaned.columns)
        self.assertNotIn("inputstate", cleaned.columns)
        self.assertNotIn("CC24_431b_1", cleaned.columns)


class TestLoaders(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_directory.name)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_load_dataframe_reads_ces_csv(self) -> None:
        frame = DataFrame({"col": [1, 2]})
        frame.to_csv(self.data_path / "ces_data.csv", index=False)

        result = load_dataframe(self.data_path)

        self.assertEqual(list(result["col"]), [1, 2])

    def test_load_dataframe_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_dataframe(self.data_path)

    def test_load_fips_data_renames_and_casts(self) -> None:
        DataFrame(
            {
                "STATE": ["26", "6"],
                "STUSAB": ["MI", "CA"],
                "STATE_NAME": ["Michigan", "California"],
                "STATENS": ["1", "2"],
            }
        ).to_csv(self.data_path / "fips.csv", index=False)

        result = load_fips_data(self.data_path)

        self.assertIn("State FIPS Code", result.columns)
        self.assertIn("State Name", result.columns)
        self.assertIn("State Code", result.columns)
        self.assertEqual(result["State FIPS Code"].dtype, np.int64)
        self.assertEqual(result.iloc[0]["State Code"], "MI")

    def test_load_voter_id_effect_reads_ncsl_csv(self) -> None:
        DataFrame(
            {
                "State Name": ["Michigan"],
                "NCSL Classification": ["Non-Strict, Photo ID"],
            }
        ).to_csv(self.data_path / "ncsl_voter_id_classification.csv", index=False)

        result = load_voter_id_effect(self.data_path)

        self.assertEqual(result.iloc[0]["State Name"], "Michigan")


class TestLoadFullDataframe(unittest.TestCase):
    def test_orchestrates_load_clean_and_merge(self) -> None:
        cfg = _model_config()
        cleaned = DataFrame(
            {
                "Education": ["No HS degree"],
                "Race": ["White"],
                "Gender": ["Man"],
                "Age": [34],
                "In person": ["Yes"],
                "Phone call": ["No"],
                "Email or text message": ["No"],
                "Letter or postcard": ["No"],
                "State FIPS Code": [26],
                "Voted": [1],
            }
        )
        fips = DataFrame(
            {
                "State FIPS Code": [26],
                "State Name": ["Michigan"],
                "State Code": ["MI"],
                "STATENS": [1],
            }
        )
        ncsl = DataFrame(
            {
                "State Name": ["Michigan"],
                "NCSL Classification": ["Non-Strict, Photo ID"],
            }
        )

        with (
            patch("capstone.data_cleaning.load_dataframe", return_value=DataFrame({"raw": [1]})) as mock_ces,
            patch("capstone.data_cleaning.clean_ces_data", return_value=cleaned) as mock_clean,
            patch("capstone.data_cleaning.load_fips_data", return_value=fips) as mock_fips,
            patch("capstone.data_cleaning.load_voter_id_effect", return_value=ncsl) as mock_ncsl,
        ):
            result = load_full_dataframe(cfg)

        mock_ces.assert_called_once_with(Path(cfg["data_path"]))
        mock_clean.assert_called_once()
        mock_fips.assert_called_once_with(Path(cfg["data_path"]))
        mock_ncsl.assert_called_once_with(Path(cfg["data_path"]))

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["State Name"], "Michigan")
        self.assertEqual(result.iloc[0]["NCSL Classification"], "Non-Strict, Photo ID")
        self.assertIn("Voted", result.columns)

    def test_drops_rows_with_missing_features(self) -> None:
        cfg = _model_config()
        cleaned = DataFrame(
            {
                "Education": ["No HS degree", None],
                "Race": ["White", "Black"],
                "Gender": ["Man", "Woman"],
                "Age": [34, 40],
                "In person": ["Yes", "No"],
                "Phone call": ["No", "No"],
                "Email or text message": ["No", "No"],
                "Letter or postcard": ["No", "No"],
                "State FIPS Code": [26, 26],
                "Voted": [1, 0],
            }
        )
        fips = DataFrame(
            {
                "State FIPS Code": [26],
                "State Name": ["Michigan"],
                "State Code": ["MI"],
                "STATENS": [1],
            }
        )
        ncsl = DataFrame(
            {
                "State Name": ["Michigan"],
                "NCSL Classification": ["Non-Strict, Photo ID"],
            }
        )

        with (
            patch("capstone.data_cleaning.load_dataframe", return_value=DataFrame()),
            patch("capstone.data_cleaning.clean_ces_data", return_value=cleaned),
            patch("capstone.data_cleaning.load_fips_data", return_value=fips),
            patch("capstone.data_cleaning.load_voter_id_effect", return_value=ncsl),
        ):
            result = load_full_dataframe(cfg)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Education"], "No HS degree")


if __name__ == "__main__":
    unittest.main()
