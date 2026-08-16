"""Tests for capstone.config constants and internal consistency."""

from __future__ import annotations

import unittest
from pathlib import Path

from capstone import config


class TestConfigConstants(unittest.TestCase):
    def test_data_path_is_path(self) -> None:
        self.assertIsInstance(config.DATA_PATH, Path)
        self.assertEqual(config.DATA_PATH, Path(".data"))

    def test_target_is_voted(self) -> None:
        self.assertEqual(config.TARGET, "Voted")

    def test_full_columns_include_outcome_and_key_features(self) -> None:
        for column in ("Voted", "Age", "Education", "State FIPS Code"):
            self.assertIn(column, config.FULL_COLUMNS)

    def test_features_are_subset_of_modeling_inputs(self) -> None:
        # FEATURES should be usable for dropna before modeling.
        for feature in config.FEATURES:
            self.assertIsInstance(feature, str)
            self.assertTrue(feature)

        self.assertIn("NCSL Classification", config.FEATURES)
        self.assertNotIn("Voted", config.FEATURES)

    def test_binary_features_are_outreach_channels(self) -> None:
        expected = {
            "In person",
            "Phone call",
            "Email or text message",
            "Letter or postcard",
        }
        self.assertEqual(set(config.BINARY_FEATURES), expected)

    def test_maps_keys_match_mapping_tables(self) -> None:
        for column, map_name in config.MAPS.items():
            self.assertTrue(hasattr(config, map_name.upper()))
            mapping = getattr(config, map_name.upper())
            self.assertIsInstance(mapping, dict)
            self.assertGreater(len(mapping), 0)
            self.assertIsInstance(column, str)

    def test_demographic_and_outreach_rename_targets_are_unique(self) -> None:
        demo_targets = list(config.DEMOGRAPHIC_COLUMNS.values())
        outreach_targets = list(config.VOTER_OUTREACH_COLUMNS.values())

        self.assertEqual(len(demo_targets), len(set(demo_targets)))
        self.assertEqual(len(outreach_targets), len(set(outreach_targets)))

    def test_state_column_maps_inputstate(self) -> None:
        self.assertEqual(config.STATE_COLUMN["inputstate"], "State FIPS Code")

    def test_outreach_mappings_include_yes_no(self) -> None:
        for mapping in (
            config.IN_PERSON_MAPPING,
            config.PHONE_MAPPING,
            config.EMAIL_MAPPING,
            config.LETTER_MAPPING,
        ):
            self.assertIn("Yes", mapping.values())
            self.assertIn("No", mapping.values())


if __name__ == "__main__":
    unittest.main()
