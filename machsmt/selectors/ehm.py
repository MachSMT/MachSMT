from machsmt.exceptions.exceptions import MachSMT_InsufficientData
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
        if len(X) < config.min_datapoints:
            raise MachSMT_InsufficientData(f"Insufficient data {len(X)=} < {config.min_datapoints=}")
        for solver in self.lm:
            self.lm[solver] = mk_regressor()
            self.lm[solver].train(X, Y[solver])

    def predict(self, benchmarks, include_predictions=False):
        super().predict(benchmarks, include_predictions)
        X, _ = self.mk_tabular_data(benchmarks)
        predicted_times = {}
        for solver, lm in self.lm.items():
            predicted_times[solver] = lm.predict(X)
        ret, ret_pred = [], []
        for it, benchmark in enumerate(benchmarks):
            pred_dict = dict(
                (self.name_to_solver(solver), predicted_times[solver][it])
                for solver in self.lm
            )
            ret.append(
                min(pred_dict, key=pred_dict.get)
            )
            ret_pred.append(
                self.score_soft_max(pred_dict)
            )
        if include_predictions:
            return ret, ret_pred
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