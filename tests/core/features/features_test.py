import unittest
import os

from typing import Callable, Iterable# Note: Make sure to checkout the 2019 release of SMT-LIB before running this

# Build models for 2019 single query data
#for csv in csv/2019/single-query/*.csv; do
#    logic=$(basename $csv)
#    logic=${logic%.csv}
#    machsmt_build -f "$csv" -l "lib-sq/2019/single-query/$logic"
#done

# Build models for 2019 incremental data
#for csv in csv/2019/incremental/*.csv; do
#    logic=$(basename $csv)
#    logic=${logic%.csv}
#    machsmt_build -f "$csv" -l "lib-inc/2019/incremental/$logic"
#done

from machsmt.features import bonus_features
from machsmt.benchmark.tokenize_sexpr import SExprTokenizer


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class FeatureTest(unittest.TestCase):
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
