import unittest
import os
from machsmt import MachSMT,DataBase
from machsmt.exceptions import MachSMT_IncompleteDataError

##"github actions" to integrate regression testing

def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit core
    os.chdir('data')


class MachSMT_Test(unittest.TestCase):
    def test_init_1(self):
        nav_to_data_dir()
        _ = MachSMT(DataBase())

    def test_init_2(self):
        nav_to_data_dir()
        _ = MachSMT('csv/large.csv')

    def test_init_3(self):
        nav_to_data_dir()
        _ = MachSMT(['csv/small.csv', 'csv/small2.csv'])

    def test_init_4(self):
        nav_to_data_dir()
        _ = MachSMT(['csv/large.csv'])

    def test_incomplete(self):
        nav_to_data_dir()
        with self.assertRaises(MachSMT_IncompleteDataError):
            _ = MachSMT(['csv/large_bug.csv'])

    def test_train_1(self):
        nav_to_data_dir()
        mach = MachSMT(['csv/large.csv'])
        mach.train()

    def test_predict_1(self):
        nav_to_data_dir()
        mach = MachSMT(['csv/large.csv'])
        mach.train()
        p = mach.predict(mach.db.get_benchmarks())
        self.assertTrue(isinstance(p, list))
        self.assertEqual(len(p), len(mach.db.get_benchmarks()))

    def test_save(self):
        nav_to_data_dir()
        self.assertTrue(not os.path.exists('main.machsmt'))
        mach = MachSMT(['csv/large.csv'])
        mach.train()
        mach.save(path=f"{os.getcwd()}/main.machsmt")
        self.assertTrue(os.path.exists('main.machsmt'))
        os.remove('main.machsmt')

    def test_load(self):
        nav_to_data_dir()
        self.assertTrue(not os.path.exists('main.machsmt'))
        mach = MachSMT(['csv/large.csv'])
        mach.train()
        mach.save(path=f"{os.getcwd()}/main.machsmt")
        self.assertTrue(os.path.exists('main.machsmt'))

        mach2 = MachSMT.load(path = f"{os.getcwd()}/main.machsmt")
        self.assertTrue(len(mach2.db) > 0)
        os.remove('main.machsmt')
        

if __name__ == '__main__':
    unittest.main()
