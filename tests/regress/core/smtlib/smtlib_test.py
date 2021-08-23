import unittest
import os
from machsmt.smtlib import grammatical_construct_list, get_theories


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class SMTLIB_Test(unittest.TestCase):
    def test_init_1(self):
        self.assertEqual(len(grammatical_construct_list), 187)

    def test_init_2(self):
        self.assertTrue('fp.fma' in grammatical_construct_list)
        self.assertTrue('assert' in grammatical_construct_list)

    def test_init_3(self):
        self.assertEqual(get_theories("QF_FP"), ['FP'])

    def test_init_3(self):
        self.assertEqual(get_theories("QF_AXFPBV"), ['A', 'BV', 'FP'])


if __name__ == '__main__':
    unittest.main()
