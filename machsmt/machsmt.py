from machsmt.benchmark.benchmark import Benchmark
from machsmt.selectors import Greedy, GreedyLogic, EHM, EHMLogic
import pdb
import pickle
import os
import lzma
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
        self.selectors['EHM'] = EHM(self.db)
        self.default_selector = 'EHM'
        if self.multi_logic:
            self.selectors['EHMLogic'] = EHMLogic(self.db)
            self.default_selector = 'EHMLogic'
        if config.greedy:
            self.selectors['Greedy'] = Greedy(self.db)
            if self.multi_logic:
                self.selectors['GreedyLogic'] = GreedyLogic(self.db)
        if config.pwc:
            raise NotImplementedError ## currently cut due to lack of performance

        self.training_scores = {}

    def train(self, benchmarks=None, eval=True):
        if benchmarks is None:
            benchmarks = self.db.get_benchmarks()
        if eval:
            predictions = {}
            for name, algo in self.selectors.items():
                predictions[name] = algo.eval(benchmarks)
            self.training_scores = dict((logic, {}) for logic in self.db.get_logics())
            for algo_name, algo_predictions in predictions.items():
                for it, solver in enumerate(algo_predictions):
                    logic = benchmarks[it].get_logic()
                    if algo_name not in self.training_scores[logic]:
                        self.training_scores[logic][algo_name] = 0.0
                    self.training_scores[logic][algo_name] += solver.get_score(benchmarks[it])
        for selector, algo in self.selectors.items():
            algo.train(benchmarks)
        print(self.training_scores)

    def predict(self, benchmarks=None, include_predictions=False, selector = None):
        if benchmarks is None:
            benchmarks = self.db.get_benchmarks()
        if isinstance(benchmarks, Benchmark): benchmarks = [benchmarks]
        if selector is None: selector = self.default_selector
        return self.selectors[selector].predict(benchmarks=benchmarks, include_predictions=include_predictions)

        # ret_solv, ret_pred = [], []

        # for it, benchmark in enumerate(benchmarks):
        #     logic = benchmark.get_logic()
        #     if selector is None:
        #         if logic in self.training_scores:
        #             selector = min(self.training_scores[logic], key=self.training_scores[logic].get)
        #         else:
        #             selector = self.default_selector 
        #     else:
        #         assert selector in self.selectors
        #     ret = self.selectors[selector].predict([benchmark], include_scores)
        #     if include_scores:
        #         ret_solv.append(ret[0][0])
        #         ret_pred.append(ret[1][0])
        #     else:
        #         ret_solv.append(ret[0])
        # if include_scores:
        #     return ret_solv, ret_pred
        # return ret_solv

    @staticmethod
    def load(path, with_db = True):
        ret = MachSMT(DataBase(build_on_init=False))
        with open(path, 'rb') as f:
            ret.selectors = pickle.load(f)
            if with_db:
                ret.db = pickle.load(f)
                ret.training_scores = pickle.load(f)
            else:
                ret.training_scores = {}
        return ret

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.selectors, f)
            pickle.dump(self.db, f)
            pickle.dump(self.training_scores, f)        
        # f.close()

        # with open(path, 'wb') as f:
        #     pickle.dump(
        #         (self.selectors, self.db, self.training_scores)
        #         , f)