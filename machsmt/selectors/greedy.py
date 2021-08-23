from .base import Selector
from ..config import config
from ..util import warning
import random
import pdb


class Greedy(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.lm = None

    def train(self, benchmarks):
        super().train(benchmarks)
        scores = dict((solver.get_name(), 0) for solver in benchmarks[0].get_solvers())
        for benchmark in benchmarks:
            for solver in benchmark.get_solvers():
                name = solver.get_name()
                scores[name] += benchmark.get_score(solver)
        self.lm = min(scores, key=scores.get)

    def predict(self, benchmarks):
        super().predict(benchmarks)
        return self.name_to_solver([self.lm] * len(benchmarks))


class GreedyLogic(Selector):
    def __init__(self, db):
        super().__init__(db)
        self.ans = dict((logic, Greedy(db)) for logic in self.db.get_logics())

    def train(self, benchmarks):
        super().train(benchmarks)
        scores = dict(
            (logic, dict((solver.get_name(), 0) for solver in benchmarks[0].get_solvers()))
            for logic in self.db.get_logics())
        for benchmark in benchmarks:
            logic = benchmark.get_logic()
            for solver in benchmark.get_solvers():
                name = solver.get_name()
                scores[logic][name] += benchmark.get_score(solver)
        for logic in self.db.get_logics():
            self.ans[logic] = min(scores[logic], key=scores[logic].get)

    def predict(self, benchmarks):
        super().predict(benchmarks)
        return self.name_to_solver([self.ans[benchmark.get_logic()] for benchmark in benchmarks])
