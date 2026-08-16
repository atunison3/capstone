"""Tests for capstone.analysis CLI entrypoint."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestAnalysisMain(unittest.TestCase):
    def test_main_runs_download_load_train_pipeline(self) -> None:
        mock_df = MagicMock(name="DataFrame")
        mock_model = MagicMock()
        mock_model.summary.return_value = "SUMMARY"

        with (
            patch("capstone.setup_project.download_ces_data") as mock_ces,
            patch("capstone.setup_project.download_state_data") as mock_state,
            patch("capstone.setup_project.install_ncsl_classification") as mock_ncsl,
            patch("capstone.helper_functions.load_model_config", return_value={"data_path": ".data"}) as mock_cfg,
            patch("capstone.data_cleaning.load_full_dataframe", return_value=mock_df) as mock_load,
            patch("capstone.logistic_regression.train_model", return_value=mock_model) as mock_train,
            patch("capstone.analysis.print") as mock_print,
            patch("capstone.helper_functions.setup_logger") as mock_logger_factory,
        ):
            mock_logger_factory.return_value = MagicMock()

            from capstone.analysis import main

            main()

        mock_ces.assert_called_once_with()
        mock_state.assert_called_once_with()
        mock_ncsl.assert_called_once_with()
        mock_cfg.assert_called_once_with()
        mock_load.assert_called_once_with({"data_path": ".data"})
        mock_train.assert_called_once_with(mock_df)
        mock_model.summary.assert_called_once_with()
        mock_print.assert_called_once_with("SUMMARY")


if __name__ == "__main__":
    unittest.main()
