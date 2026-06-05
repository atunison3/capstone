import unittest

from src.main import foo


class TestMain(unittest.TestCase):
    def test01(self):
        test_string = foo()

        self.assertEqual(test_string, "Hello World")


if __name__ == "__main__":
    unittest.main()
