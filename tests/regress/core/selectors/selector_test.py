import unittest
import os
from machsmt.selectors import Greedy, GreedyLogic
from machsmt.database import DataBase


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class PredictorTest(unittest.TestCase):
    def test_init(self):
        Greedy(DataBase())
        GreedyLogic(DataBase())


if __name__ == '__main__':
    unittest.main()
