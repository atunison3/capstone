import unittest
from pathlib import Path

from capstone.helper_functions import load_ces_data, load_config, load_fips_data


class TestHelperFunctions(unittest.TestCase):
    def test_001_load_config(self):

        config = load_config()

        self.assertEqual(config["x"], 1)

    def test_002_load_ces_data(self):

        data_path = Path("data/test/data.csv")
        df = load_ces_data(data_path)

        self.assertEqual(len(df), 50)

    def test_003_load_fips_data(self):

        fips_df = load_fips_data()

        self.assertEqual(len(fips_df), 51)


if __name__ == "__main__":
    unittest.main()
