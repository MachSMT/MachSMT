import unittest
import os

from typing import Callable, Iterable

from machsmt.features import bonus_features
from machsmt.tokenize_sexpr import SExprTokenizer


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class RegressorTest(unittest.TestCase):
    def test_features_1(self):
        self.assertEqual(type(bonus_features), list)
        self.assertTrue(len(bonus_features) > 0)
        for feature in bonus_features:
            self.assertTrue(isinstance(feature, Callable))

    def test_features_2(self):
        nav_to_data_dir()
        for feature in bonus_features:
            ret = feature(SExprTokenizer('benchmarks/a.smt2'))

    def test_features_3(self):
        nav_to_data_dir()
        for feature in bonus_features:
            ret = feature(SExprTokenizer('benchmarks/b.smt2'))


if __name__ == '__main__':
    unittest.main()
