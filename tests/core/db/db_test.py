import unittest
import os
from machsmt.database import DataBase
from machsmt.exceptions import MachSMT_BadCSVError, MachSMT_IncompleteDataError

def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class DatabaseTest(unittest.TestCase):
    def test_init(self):
        db = DataBase()

    def test_init_2(self):
        with self.assertRaises(FileNotFoundError):
            DataBase('asdf')

    def test_init_2(self):
        with self.assertRaises(FileNotFoundError):
            DataBase(['csv/small.csv', 'csv/small2.csv', 'asdf'])

    def test_parse_csv_file(self):
        nav_to_data_dir()
        db = DataBase()
        db.parse_csv_file(f'csv/small.csv')
        logics = db.get_logics()
        benchmarks = db.get_benchmarks()
        solvers = db.get_solvers()
        self.assertEqual(len(logics), 1)
        self.assertEqual(logics[0], 'UNPARSED')
        self.assertEqual(len(solvers), 2)
        self.assertEqual(len(benchmarks), 2)

    def test_parse_csv_file_bad(self):
        with self.assertRaises(MachSMT_BadCSVError):
            nav_to_data_dir()
            db = DataBase()
            db.parse_csv_file(f'csv/small_bad_head.csv')
            logics = db.get_logics()
            benchmarks = db.get_benchmarks()
            solvers = db.get_solvers()
            self.assertEqual(len(logics), 1)
            self.assertEqual(logics[0], 'UNPARSED')
            self.assertEqual(len(solvers), 2)
            self.assertEqual(len(benchmarks), 2)

    def test_build_empty(self):
        nav_to_data_dir()
        db = DataBase()
        db.build()

    def test_build_small_1(self):
        nav_to_data_dir()
        db = DataBase()
        db.build(f'csv/small.csv')
        logics = db.get_logics()
        benchmarks = db.get_benchmarks()
        solvers = db.get_solvers()
        self.assertEqual(len(logics), 1)
        self.assertEqual(logics[0], 'QF_FP')
        for benchmark in db.get_benchmarks():
            self.assertTrue(len(benchmark.get_features()) > 30)
        self.assertEqual(len(solvers), 2)
        self.assertEqual(len(benchmarks), 2)

    def test_build_small_2(self):
        nav_to_data_dir()
        db = DataBase(f'csv/small.csv')
        logics = db.get_logics()
        benchmarks = db.get_benchmarks()
        solvers = db.get_solvers()
        self.assertEqual(len(logics), 1)
        self.assertEqual(logics[0], 'QF_FP')
        for benchmark in db.get_benchmarks():
            self.assertTrue(len(benchmark.get_features()) > 30)
        self.assertEqual(len(solvers), 2)
        self.assertEqual(len(benchmarks), 2)

    def test_build_small_3(self):
        nav_to_data_dir()
        db = DataBase(['csv/small.csv', 'csv/small2.csv'])
        logics = db.get_logics()
        benchmarks = db.get_benchmarks()
        solvers = db.get_solvers()
        self.assertEqual(len(logics), 1)
        self.assertEqual(logics[0], 'QF_FP')
        for benchmark in db.get_benchmarks():
            self.assertTrue(len(benchmark.get_features()) > 30)
        self.assertEqual(len(solvers), 2)
        self.assertEqual(len(benchmarks), 4)

    def test_build_large(self):
        nav_to_data_dir()
        db = DataBase('csv/large.csv')
        logics = db.get_logics()
        benchmarks = db.get_benchmarks()
        solvers = db.get_solvers()
        self.assertEqual(len(logics), 2)
        self.assertEqual(logics[0], 'QF_BV')
        self.assertEqual(logics[1], 'QF_FP')
        for benchmark in db.get_benchmarks():
            self.assertTrue(len(benchmark.get_features()) > 30)
            self.assertEqual(len(benchmark.get_solvers()), 2)
        self.assertEqual(len(solvers), 2)
        self.assertEqual(len(benchmarks), 26)

    def test_save_load(self):
        nav_to_data_dir()
        if os.path.isfile('db.machsmt'):
            print("Deleting File")
            os.remove('db.machsmt')
        self.assertFalse(os.path.isfile('db.machsmt'))
        db = DataBase(['csv/small.csv', 'csv/small2.csv'])
        db.save(os.getcwd())
        self.assertTrue(os.path.isfile('db.machsmt'))
        db2 = DataBase()
        with self.assertRaises(FileNotFoundError):
            db2.load(loc=os.getcwd(), name='test.machsmt')
        db2.load(loc=os.getcwd())

        logics = db2.get_logics()
        benchmarks = db2.get_benchmarks()
        solvers = db2.get_solvers()
        self.assertEqual(len(logics), 1)
        self.assertEqual(logics[0], 'QF_FP')
        for benchmark in db2.get_benchmarks():
            self.assertTrue(len(benchmark.get_features()) > 30)
        self.assertEqual(len(solvers), 2)
        self.assertEqual(len(benchmarks), 4)


if __name__ == '__main__':
    unittest.main()
