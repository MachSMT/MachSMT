import unittest
import os
from machsmt.solver import Solver
from machsmt.benchmark import Benchmark


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class SolverTest(unittest.TestCase):
    def test_init_1(self):
        Solver('test')

    def test_init_2(self):
        nav_to_data_dir()
        b = Benchmark('benchmarks/a.smt2')
        b.parse()
        s = Solver('test')
        s.add_benchmark(b, 1234)
        self.assertTrue(b in s)
        self.assertEqual(s[b], 1234)
        self.assertEqual(s.get_logics(), ['QF_FP'])
        s.remove_benchmark(b)
        self.assertTrue(b not in s)


if __name__ == '__main__':
    unittest.main()
