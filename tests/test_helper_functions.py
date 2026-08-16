import logging
import tempfile
import unittest
from logging.handlers import RotatingFileHandler
from pathlib import Path
from unittest.mock import patch

from capstone import config
from capstone import helper_functions as fun
from capstone.helper_functions import (
    detect_source_tree_root,
    expand_user,
    load_model_config,
    resolve_data_path,
    setup_logger,
)


class TestLoadConfig(unittest.TestCase):
    """Tests for load_model_config(), which exposes UPPERCASE config constants as a dict."""

    def test_returns_dict(self) -> None:
        result = load_model_config()

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_keys_are_lowercase_uppercase_constants(self) -> None:
        result = load_model_config()

        expected_keys = {name.lower() for name in vars(config) if name.isupper()}

        self.assertEqual(set(result.keys()), expected_keys)
        for key in result:
            self.assertEqual(key, key.lower())

    def test_excludes_non_uppercase_names(self) -> None:
        result = load_model_config()

        # Module dunders / imports must not appear as config keys.
        self.assertNotIn("__name__", result)
        self.assertNotIn("__doc__", result)
        self.assertNotIn("path", result)  # from pathlib import Path

    def test_expected_analysis_keys_present(self) -> None:
        result = load_model_config()

        expected = {
            "data_path",
            "full_columns",
            "categorical_features",
            "multiclass_features",
            "binary_features",
            "features",
            "target",
            "demographic_columns",
            "voter_outreach_columns",
            "state_column",
            "maps",
            "educ_mapping",
            "race_mapping",
            "gender_mapping",
            "in_person_mapping",
            "phone_mapping",
            "email_mapping",
            "letter_mapping",
        }

        self.assertTrue(expected.issubset(result.keys()))

    def test_core_value_types_and_contents(self) -> None:
        result = load_model_config()

        self.assertIsInstance(result["full_columns"], list)
        self.assertIn("Voted", result["full_columns"])

        self.assertIsInstance(result["features"], list)
        self.assertIn("NCSL Classification", result["features"])

        self.assertEqual(result["target"], "Voted")

        self.assertIsInstance(result["demographic_columns"], dict)
        self.assertEqual(result["demographic_columns"]["educ"], "Education")

        self.assertIsInstance(result["maps"], dict)
        self.assertEqual(result["maps"]["Education"], "educ_mapping")

        self.assertEqual(result["educ_mapping"][1], "No HS degree")
        self.assertEqual(result["in_person_mapping"][1.0], "Yes")

    def test_result_is_independent_shallow_copy_of_mappings(self) -> None:
        """Top-level dict should be a new mapping each call; values are the module objects."""
        first = load_model_config()
        second = load_model_config()

        self.assertIsNot(first, second)
        self.assertEqual(first, second)

        # Values are taken directly from the config module (same object identity).
        self.assertIs(first["features"], config.FEATURES)
        self.assertIs(first["demographic_columns"], config.DEMOGRAPHIC_COLUMNS)


class TestResolveDataPath(unittest.TestCase):
    def test_relative_path_defaults_to_explicit_project_root_when_missing(self) -> None:
        root = Path("/tmp/fake-project")  # nosec: B108
        result = resolve_data_path(".data", project_root=root, cwd=Path("/tmp/other-cwd"))  # nosec: B108
        self.assertEqual(result, (root / ".data").resolve())

    def test_absolute_path_unchanged_aside_from_resolve(self) -> None:
        absolute = Path("/var/data/ces").resolve()
        result = resolve_data_path(absolute, project_root=Path("/tmp/other"))  # nosec: B108
        self.assertEqual(result, absolute)

    def test_prefers_existing_cwd_over_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            cwd = base / "cwd"
            root = base / "root"
            cwd.mkdir()
            root.mkdir()
            (cwd / ".data").mkdir()
            (root / ".data").mkdir()

            result = resolve_data_path(".data", project_root=root, cwd=cwd)

        self.assertEqual(result, (cwd / ".data").resolve())

    def test_uses_project_root_when_only_root_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            cwd = base / "cwd"
            root = base / "root"
            cwd.mkdir()
            root.mkdir()
            (root / ".data").mkdir()

            result = resolve_data_path(".data", project_root=root, cwd=cwd)

        self.assertEqual(result, (root / ".data").resolve())

    def test_installed_package_without_source_tree_uses_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            with patch("capstone.helper_functions.detect_source_tree_root", return_value=None):
                result = resolve_data_path(".data", cwd=cwd)

        self.assertEqual(result, (cwd / ".data").resolve())
        self.assertNotIn("site-packages", str(result))

    def test_detect_source_tree_root_finds_repo(self) -> None:
        root = detect_source_tree_root()
        # Running tests from this repository should detect the source tree.
        self.assertIsNotNone(root)
        if not root:
            raise TypeError
        self.assertTrue((root / "pyproject.toml").is_file())
        self.assertTrue((root / "capstone").is_dir())


class TestExpandUser(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_directory.name)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_returns_resolved_existing_path(self) -> None:
        result = expand_user(self.temp_path)

        self.assertEqual(result, self.temp_path.resolve())
        self.assertTrue(result.is_absolute())

    def test_returns_existing_file_path(self) -> None:
        file_path = self.temp_path / "config.toml"
        file_path.write_text('data_path = "data"', encoding="utf-8")

        result = expand_user(file_path)

        self.assertEqual(result, file_path.resolve())

    def test_missing_path_raises_file_not_found_error(self) -> None:
        missing_path = self.temp_path / "missing"

        with self.assertRaisesRegex(
            FileNotFoundError,
            "Configuration file not found",
        ):
            expand_user(missing_path)

    def test_expands_tilde_path(self) -> None:
        expected_path = self.temp_path.resolve()

        with patch.object(
            Path,
            "expanduser",
            return_value=expected_path,
        ) as mock_expanduser:
            result = expand_user(Path("~/data"))

        self.assertEqual(result, expected_path)
        mock_expanduser.assert_called_once()


class TestSetupLogger(unittest.TestCase):
    def tearDown(self) -> None:
        logger = logging.getLogger("test_capstone")

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def test_setup_logger(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / ".log"

            with patch.object(fun, "LOG_DIR", log_dir):
                logger = setup_logger("test_capstone")

                self.assertTrue(log_dir.exists())
                self.assertTrue(log_dir.is_dir())

                self.assertEqual(logger.name, "test_capstone")
                self.assertEqual(logger.level, logging.DEBUG)
                self.assertEqual(len(logger.handlers), 2)

                console_handler = next(handler for handler in logger.handlers if type(handler) is logging.StreamHandler)
                file_handler = next(handler for handler in logger.handlers if isinstance(handler, RotatingFileHandler))

                self.assertEqual(console_handler.level, logging.INFO)
                self.assertEqual(file_handler.level, logging.DEBUG)

                self.assertEqual(file_handler.maxBytes, 5 * 1024 * 1024)
                self.assertEqual(file_handler.backupCount, 5)

                logger.info("Test log message")

                for handler in logger.handlers:
                    handler.flush()

                log_path = log_dir / "capstone.log"

                self.assertTrue(log_path.exists())
                self.assertIn("Test log message", log_path.read_text(encoding="utf-8"))

    def test_setup_logger_does_not_duplicate_handlers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / ".log"

            with patch.object(fun, "LOG_DIR", log_dir):
                logger = setup_logger("test_capstone")
                initial_handlers = logger.handlers.copy()

                same_logger = setup_logger("test_capstone")

                self.assertIs(logger, same_logger)
                self.assertEqual(logger.handlers, initial_handlers)
                self.assertEqual(len(logger.handlers), 2)


if __name__ == "__main__":
    unittest.main()
