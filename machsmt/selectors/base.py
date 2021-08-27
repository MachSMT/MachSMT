from ..benchmark import Benchmark
from ..config import config
import numpy as np
import pdb
from sklearn.model_selection import KFold

class Selector:
    def __init__(self, db):
        self.db = db

    def train(self, benchmarks):
        assert len(benchmarks) > 0

    def predict(self, benchmarks, include_predictions):
        assert len(benchmarks) > 0

    def eval(self, benchmarks):
        assert len(benchmarks) > 0
        np_bench = np.array(benchmarks)
        ret = [None for _ in benchmarks]
        k_fold_args = {'n_splits': config.k, 'shuffle': True, 'random_state': config.rng}
        for train, test in KFold(**k_fold_args).split(np_bench):
            self.train(benchmarks=np_bench[train])
            pred = self.predict(np_bench[test])
            for it, indx in enumerate(test):
                ret[indx] = pred[it]
        return ret

    def mk_tabular_data(self, benchmarks):
        X_out, Y_out = [], dict((solver.get_name(), []) for solver in self.db.get_solvers())
        for benchmark in benchmarks:
            X_out.append(benchmark.get_features())
            for solver in benchmark.get_solvers():
                score = benchmark.get_score(solver) + 1
                if score > config.max_score:
                    score = 5 * config.max_score
                Y_out[solver.get_name()].append(score)
        X_out = np.array(X_out)
        for solver in self.db.get_solvers():
            Y_out[solver.get_name()] = np.log(np.array(Y_out[solver.get_name()]).reshape(-1, 1))
        return X_out, Y_out

    def name_to_solver(self, names):
        return [self.db.get_solver(name) for name in names]

    def score_soft_max(self, data):
        if isinstance(data, list):
            return [self.score_soft_max(v) for v in data]
        elif isinstance(data, dict):
            denon = sum(np.exp(v) for v in data.values())
            for key in data:
                data[key] = np.exp(data[key]) / denon
            return data