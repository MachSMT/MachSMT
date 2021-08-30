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

        #convert 
        self.score_flip = dict((solver, -score) for solver, score in self.scores.items())
        low, high = min(self.score_flip.values()), max(self.score_flip.values())
        for solver in self.score_flip: self.score_flip[solver] = (self.score_flip[solver] - low) / (high - low)

    def predict(self, benchmarks, include_predictions=False):
        super().predict(benchmarks, include_predictions)
        ret = self.name_to_solver([self.best] * len(benchmarks))
        if include_predictions:
            return ret, [self.score_soft_max(self.score_flip)] * len(benchmarks)
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
            ret = self.lm[benchmark.get_logic()].predict()
            if include_predictions:
                ret_solver.append(ret[0])
                ret_predictions.append(ret[0])
            else:
                ret_solver.append(ret)
        if include_predictions:
            return ret_solver, ret_predictions
        return ret_solver
