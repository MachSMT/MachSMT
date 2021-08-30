from machsmt import benchmark
from machsmt.selectors import Greedy, GreedyLogic, EHM, EHMLogic
import pdb
import pickle
import os
from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np

# from .predictors import Random, Oracle, Greedy, Solver, SolverLogic
from .util import warning, die
from .config import config
from .database import DataBase
from .exceptions import MachSMT_IncompleteDataError


class MachSMT:
    def __init__(self, data):
        if isinstance(data, DataBase):
            self.db = data
        elif isinstance(data, (str, os.PathLike)):
            self.db = DataBase(data)
        elif isinstance(data, Iterable):
            for v in data:
                if not isinstance(v, (str, os.PathLike)):
                    die(f"Unexpected value: {v}")
            self.db = DataBase(data)
        else:
            die(f"Unexpected value: {data}")
        if not self.db.is_complete():
            raise MachSMT_IncompleteDataError

        self.multi_logic = len(self.db.get_logics()) > 1

        self.selectors = {}
        # self.selectors['EHM'] = EHM(self.db)
        # if self.multi_logic:
        #     self.selectors['EHMLogic'] = EHMLogic(self.db)
        if config.greedy:
            self.selectors['Greedy'] = Greedy(self.db)
            if self.multi_logic:
                self.selectors['GreedyLogic'] = GreedyLogic(self.db)
        if config.pwc:
            raise NotImplementedError ## currently cut due to lack of performance
        self.training_scores = {}

    def train(self, benchmarks=None):
        if benchmarks is None:
            benchmarks = self.db.get_benchmarks()
        predictions = dict(
            (name, algo.eval(benchmarks))
            for name, algo in self.selectors.items())
        predictions = {}
        for name, algo in self.selectors.items():
            predictions[name] = algo.eval(benchmarks)
        self.training_scores = {}
        for algo_name, algo_predictions in predictions.items():
            self.training_scores[algo_name] = 0
            for it, solver in enumerate(algo_predictions):
                self.training_scores[algo_name] += solver.get_score(benchmarks[it])
        
    def predict(self, benchmarks=None, include_scores = False):
        if benchmarks is None:
            benchmarks = self.db.get_benchmarks()        
        best_selector = min(self.training_scores, key=self.training_scores.get)
        return self.selectors[best_selector].predict(benchmarks, include_scores)

    @staticmethod
    def load(path):
        f = open(path, 'rb')
        tmp_dict = pickle.load(f)
        f.close()          
        ret = MachSMT(DataBase(build_on_init=False))
        ret.__dict__.update(tmp_dict) 
        return ret

    def save(self, path):
        f = open(path, 'wb')
        pickle.dump(self.__dict__, f)
        f.close()