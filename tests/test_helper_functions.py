import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from capstone.helper_functions import load_config


class TestLoadTomlConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_directory.name)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def write_config(
        self,
        content: str,
        filename: str = "config.toml",
    ) -> Path:
        """Create a temporary TOML file and return its path."""
        config_path = self.temp_path / filename
        config_path.write_text(content, encoding="utf-8")
        return config_path

    def test_loads_valid_toml_file(self) -> None:
        config_path = self.write_config(
            """
            data_path = "data/data-prod"

            [model]
            random_state = 42
            test_size = 0.20
            """
        )

        result = load_config(config_path)

        expected = {
            "data_path": "data/data-prod",
            "model": {
                "random_state": 42,
                "test_size": 0.20,
            },
        }

        self.assertEqual(result, expected)

    def test_accepts_path_object(self) -> None:
        config_path = self.write_config(
            """
            version = 1
            data_path = "P-value Patriots are Awesome!"
            """
        )

        result = load_config(config_path)

        self.assertEqual(result, {"version": 1, "data_path": "P-value Patriots are Awesome!"})

    def test_loads_supported_toml_data_types(self) -> None:
        config_path = self.write_config(
            """
            name = "example"
            enabled = true
            count = 10
            threshold = 0.75
            tags = ["data", "modeling"]
            data_path = "hello/world"

            [database]
            host = "localhost"
            port = 5432
            """
        )

        result = load_config(config_path)

        self.assertEqual(result["name"], "example")
        self.assertTrue(result["enabled"])
        self.assertEqual(result["count"], 10)
        self.assertEqual(result["threshold"], 0.75)
        self.assertEqual(result["tags"], ["data", "modeling"])
        self.assertEqual(result["database"]["host"], "localhost")
        self.assertEqual(result["database"]["port"], 5432)
        self.assertEqual(result["data_path"], "hello/world")

    def test_missing_file_raises_file_not_found_error(self) -> None:
        missing_path = self.temp_path / "missing.toml"

        with self.assertRaisesRegex(
            FileNotFoundError,
            "Configuration file not found",
        ):
            load_config(missing_path)

    def test_directory_path_raises_is_a_directory_error(self) -> None:
        with self.assertRaisesRegex(
            IsADirectoryError,
            "Configuration path is not a file",
        ):
            load_config(self.temp_path)

    def test_invalid_toml_raises_decode_error(self) -> None:
        config_path = self.write_config(
            """
            [model
            random_state = 42
            """
        )

        with self.assertRaises(tomllib.TOMLDecodeError):
            load_config(config_path)

    def test_duplicate_keys_raise_decode_error(self) -> None:
        config_path = self.write_config(
            """
            random_state = 42
            random_state = 100
            data_path = "."
            """
        )

        with self.assertRaises(tomllib.TOMLDecodeError):
            load_config(config_path)

    def test_expands_user_home_directory(self) -> None:
        config_path = self.write_config(
            """
                environment = "test"
                data_path = "."
            """
        )

        with patch.object(
            Path,
            "expanduser",
            return_value=config_path,
        ) as mock_expanduser:
            result = load_config("~/config.toml")  # type: ignore

        self.assertEqual(result, {"environment": "test", "data_path": "."})
        mock_expanduser.assert_called_once()

    def test_preserves_unicode_values(self) -> None:
        config_path = self.write_config(
            """
            data_path = "."
            greeting = "สวัสดี"
            city = "Genova"
            """
        )

        result = load_config(config_path)

        self.assertEqual(result["greeting"], "สวัสดี")
        self.assertEqual(result["city"], "Genova")

    def test_filename_with_spaces(self) -> None:
        config_path = self.write_config(
            """
            project = "election analysis"
            data_path = "."
            """,
            filename="project config.toml",
        )

        result = load_config(config_path)

        self.assertEqual(result, {"project": "election analysis", "data_path": "."})

    def test_missing_data_path_raises_key_error(self) -> None:
        config_path = self.write_config(
            """
            [model]
            random_state = 42
            """
        )

        with self.assertRaises(KeyError):
            load_config(config_path)


if __name__ == "__main__":
    unittest.main()
