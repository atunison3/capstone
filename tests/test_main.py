import unittest


class TestMain(unittest.TestCase):
    def test01(self):
        test_string = "Hello World"

        self.assertEqual(test_string, "Hello World")


if __name__ == "__main__":
    unittest.main()
