import unittest

from machsmt.util import warning, die


class UtilTest(unittest.TestCase):
    def test_features_1(self):
        with self.assertRaises(SystemExit):
            die("test")

    def test_features_2(self):
        warning("test")


if __name__ == '__main__':
    unittest.main()
