import numpy as np
from .base import Selector
from ..config import config
from ..util import warning
from ..ml import mk_regressor
import random
import pdb


class EHM(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.lm = dict((solver.get_name(), None) for solver in self.db.get_solvers())

    def train(self, benchmarks):
        super().train(benchmarks)
        X, Y = self.mk_tabular_data(benchmarks)
        for solver in self.lm:
            self.lm[solver] = mk_regressor()
            self.lm[solver].train(X, Y[solver])

    def predict(self, benchmarks):
        super().predict(benchmarks)
        ret = [None for _ in benchmarks]
        solvers = sorted(self.lm.keys())
        X, _ = self.mk_tabular_data(benchmarks)
        predicted_times = {}
        for solver, lm in self.lm.items():
            predicted_times[solver] = lm.predict(X)
        for it, bench in enumerate(benchmarks):
            bench_predictions = [predicted_times[solver][it] for solver in solvers]
            ret[it] = self.db.get_solver(solvers[np.argmin(bench_predictions)])
        return ret


class EHMLogic(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.lm = dict((logic, EHM(self.db)) for logic in db.get_logics())

    def train(self, benchmarks):
        super().train(benchmarks)
        logic_benchmark = dict((logic, []) for logic in self.lm)
        for benchmark in benchmarks:
            logic_benchmark[benchmark.get_logic()].append(benchmark)
        for logic in self.lm:
            self.lm[logic].train(logic_benchmark[logic])

    def predict(self, benchmarks):
        super().predict(benchmarks)
        ret = []
        for benchmark in benchmarks:
            ret.append(
                self.lm[benchmark.get_logic()].predict([benchmark])[0]
            )
        return ret
