from machsmt.exceptions.exceptions import MachSMT_InsufficientData
import numpy as np
from .base import Selector
from ..config import args
from ..util import warning
from ..ml import mk_classifier
import random
import pdb


class PWC(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.lms = mk_classifier()
        self.solvers = sorted(self.db.get_solvers())
        self.solver2idx = dict((solver, idx) for idx, solver in enumerate(self.solvers))

    def train(self, benchmarks):
        super().train(benchmarks)
        X, Y = self.mk_tabular_data(benchmarks)
        self.lms = [[None for _ in self.solvers] for _ in self.solvers]
        for it in range(len(self.solvers)):
            for jt in range(it+1, len(self.solvers)):
                self.lms[it][jt] = mk_classifier()
                Y_ = [1 if y[it] < y[jt] else 0 for y in Y]
                self.lms[it][jt].fit(X, Y_)
        if len(X) < args.min_datapoints:
            raise MachSMT_InsufficientData(f"Insufficient data len(X)={len(X)} < args.min_datapoints={args.min_datapoints}")

    def predict(self, benchmarks, include_predictions=False):
        super().predict(benchmarks, include_predictions)
        ret, ret_pred = [], []
        X, _ = self.mk_tabular_data(benchmarks)
        for it, benchmark in enumerate(benchmarks):
            tallies = {solver: 0 for solver in self.solvers}
            for jt, solver1 in enumerate(self.solvers):
                for kt, solver2 in enumerate(self.solvers):
                    lm = self.lms[jt][kt]
                    if lm is None: continue
                    p = lm.predict(X[it].reshape(1, -1))[0]
                    if p: tallies[solver1] += 1
                    else: tallies[solver2] += 1
            pred_dict = {solver:tally for solver, tally in tallies.items()}
            ret.append(
                min(pred_dict, key=pred_dict.get)
            )
            ret_pred.append(
                self.score_softmin(pred_dict)
            )
        if include_predictions:
            return ret, ret_pred
        return ret

class PWCLogic(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.lm = dict((logic, PWC(self.db)) for logic in db.get_logics())

    def train(self, benchmarks):
        super().train(benchmarks)
        logic_benchmark = dict((logic, []) for logic in self.lm)
        for benchmark in benchmarks:
            logic_benchmark[benchmark.get_logic()].append(benchmark)
        for logic in self.lm:
            self.lm[logic].train(logic_benchmark[logic])

    def predict(self, benchmarks, include_predictions=False):
        super().predict(benchmarks, include_predictions)
        ret_solver, ret_predictions = [], []
        for benchmark in benchmarks:
            ret = self.lm[benchmark.get_logic()].predict([benchmark], include_predictions=include_predictions)
            if include_predictions:
                ret_solver.append(ret[0][0])
                ret_predictions.append(ret[1][0])
            else:
                ret_solver.append(ret[0])
        if include_predictions:
            return ret_solver, ret_predictions
        return ret_solver
