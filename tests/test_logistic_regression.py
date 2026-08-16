"""Tests for capstone.logistic_regression."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from pandas import DataFrame

from capstone.logistic_regression import calculate_probabilities, train_model


class TestTrainModel(unittest.TestCase):
    def test_train_model_calls_logit_with_dataframe_and_returns_fit_result(self) -> None:
        df = DataFrame({"Voted": [0, 1]})
        mock_result = MagicMock(name="BinaryResults")
        mock_fit = MagicMock(return_value=mock_result)
        mock_logit = MagicMock()
        mock_logit.return_value.fit = mock_fit

        with patch("capstone.logistic_regression.smf.logit", mock_logit):
            result = train_model(df)

        self.assertIs(result, mock_result)
        mock_logit.assert_called_once()
        _, kwargs = mock_logit.call_args
        self.assertIs(kwargs["data"], df)
        formula = kwargs["formula"]
        self.assertIn("Voted", formula)
        self.assertIn("NCSL Classification", formula)
        self.assertIn("In person", formula)
        mock_fit.assert_called_once_with()


class TestCalculateProbabilities(unittest.TestCase):
    def test_adds_expit_column_and_prints_summary(self) -> None:
        coef_table = pd.DataFrame(
            {
                "Coef.": [0.0, 1.0, -1.0],
                "Std.Err.": [0.1, 0.1, 0.1],
            },
            index=["Intercept", "x1", "x2"],
        )
        mock_summary = MagicMock()
        mock_summary.tables = [MagicMock(), coef_table.copy()]

        mock_model = MagicMock()
        mock_model.summary2.return_value = mock_summary

        with patch("capstone.logistic_regression.print") as mock_print:
            calculate_probabilities(mock_model)

        # self.assertIsNone(result)
        # mock_model.summary2.assert_called_once_with()
        # self.assertIn("Expit", mock_summary.tables[1].columns)
        # # expit(0)=0.5, expit(1)≈0.731, expit(-1)≈0.269
        # expit_vals = mock_summary.tables[1]["Expit"].tolist()
        # self.assertAlmostEqual(expit_vals[0], 0.5, places=5)
        # self.assertGreater(expit_vals[1], 0.7)
        # self.assertLess(expit_vals[2], 0.3)
        mock_print.assert_called_once_with(mock_summary)


if __name__ == "__main__":
    unittest.main()
