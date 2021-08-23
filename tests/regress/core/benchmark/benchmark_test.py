import unittest
import os
from machsmt.benchmark import Benchmark


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class BenchmarkTest(unittest.TestCase):
    def test_init_1(self):
        nav_to_data_dir()
        a = Benchmark('benchmarks/a.smt2')
        self.assertEqual(a.logic, 'UNPARSED')
        self.assertTrue(not a.parsed)

    def test_init_2(self):
        nav_to_data_dir()
        with self.assertRaises(FileNotFoundError):
            Benchmark('asdf')

    def test_logic(self):
        nav_to_data_dir()
        a = Benchmark('benchmarks/a.smt2')
        a.parse()
        self.assertEqual(a.get_logic(), 'QF_FP')

    def test_compute_features(self):
        nav_to_data_dir()
        a = Benchmark('benchmarks/a.smt2')
        self.assertEqual(type(a.get_features()), list)
        self.assertEqual(len(a.get_features()), 0)

        a.parse()

        self.assertEqual(len(a.get_features()) > 100, True)
        self.assertEqual(type(a.get_features()), list)

if __name__ == '__main__':
    unittest.main()
