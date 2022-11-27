from .base import Selector
from ..config import config
from ..util import warning

class Greedy(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.scores = {}
        self.best = None

    def train(self, benchmarks):
        super().train(benchmarks)
        self.scores = dict((solver.get_name(), 0) for solver in benchmarks[0].get_solvers())
        for benchmark in benchmarks:
            for solver in benchmark.get_solvers():
                name = solver.get_name()
                self.scores[name] += benchmark.get_score(solver)

        self.best = min(self.scores, key=self.scores.get)

    def predict(self, benchmarks, include_predictions=False):
        super().predict(benchmarks, include_predictions)
        ret = self.name_to_solver([self.best] * len(benchmarks))
        if include_predictions:
            return ret, [self.score_softmin(self.scores, negate=True)] * len(benchmarks)
        return self.name_to_solver([self.best] * len(benchmarks))

class GreedyLogic(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.lm = dict((logic, Greedy(db)) for logic in self.db.get_logics())

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
            ret = self.lm[benchmark.get_logic()].predict([benchmark])
            if include_predictions:
                ret_solver.append(ret[0][0])
                ret_predictions.append(ret[1][0])
            else:
                ret_solver.append(ret[0])
        if include_predictions:
            return ret_solver, ret_predictions
        return ret_solver
