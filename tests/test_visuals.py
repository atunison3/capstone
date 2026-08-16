"""Tests for capstone.visualization.visuals helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import DataFrame

from capstone.visualization.visuals import (
    OUTPUT_DIR,
    PROJECT_ROOT,
    ColorScheme,
    compute_turnout_by_category,
    ensure_output_dir,
)


class TestColorScheme(unittest.TestCase):
    def test_um_palette_hex_values(self) -> None:
        self.assertEqual(ColorScheme.UM_BLUE, "#00274C")
        self.assertEqual(ColorScheme.UM_MAIZE, "#FFCB05")
        self.assertTrue(str(ColorScheme.UM_BLUE).startswith("#"))


class TestOutputPaths(unittest.TestCase):
    def test_output_dir_is_under_docs_assets(self) -> None:
        self.assertEqual(OUTPUT_DIR, PROJECT_ROOT / "docs" / "assets")
        self.assertTrue(OUTPUT_DIR.is_absolute())

    def test_ensure_output_dir_creates_parents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "a" / "b" / "assets"
            result = ensure_output_dir(target)

            self.assertEqual(result, target)
            self.assertTrue(target.is_dir())


class TestComputeTurnoutByCategory(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = DataFrame(
            {
                "Contacted": [
                    "Contacted",
                    "Contacted",
                    "Contacted",
                    "Contacted",
                    "Not Contacted",
                    "Not Contacted",
                    "Not Contacted",
                    "Not Contacted",
                ],
                "Voted": [1, 1, 1, 0, 1, 0, 0, 0],
            }
        )
        self.order = ["Not Contacted", "Contacted"]

    def test_counts_and_percentages(self) -> None:
        result = compute_turnout_by_category(self.frame, "Contacted", self.order)

        self.assertListEqual(list(result.index), self.order)
        self.assertEqual(int(result.loc["Contacted", "n"]), 4)  # type: ignore
        self.assertEqual(int(result.loc["Not Contacted", "n"]), 4)  # type: ignore
        self.assertAlmostEqual(float(result.loc["Contacted", "pct"]), 75.0)  # type: ignore
        self.assertAlmostEqual(float(result.loc["Not Contacted", "pct"]), 25.0)  # type: ignore

    def test_ci_matches_wald_formula(self) -> None:
        result = compute_turnout_by_category(self.frame, "Contacted", self.order)

        p = 0.75
        n = 4
        expected = 1.96 * np.sqrt(p * (1 - p) / n) * 100
        self.assertAlmostEqual(float(result.loc["Contacted", "ci"]), expected)  # type: ignore

    def test_missing_category_in_order_is_nan_row(self) -> None:
        order = ["Not Contacted", "Contacted", "Unknown"]
        result = compute_turnout_by_category(self.frame, "Contacted", order)

        self.assertTrue(pd.isna(result.loc["Unknown", "n"]))
        self.assertTrue(pd.isna(result.loc["Unknown", "pct"]))

    def test_empty_frame_reindexes_to_order(self) -> None:
        empty = DataFrame({"Contacted": pd.Series(dtype=str), "Voted": pd.Series(dtype=int)})
        result = compute_turnout_by_category(empty, "Contacted", self.order)

        self.assertListEqual(list(result.index), self.order)


if __name__ == "__main__":
    unittest.main()
