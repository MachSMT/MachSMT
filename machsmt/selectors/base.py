from ..benchmark import Benchmark
from ..config import args
import numpy as np
import pdb
from alive_progress import alive_bar
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
        k_fold_args = {'n_splits': args.k, 'shuffle': True, 'random_state': args.rng}
        with alive_bar(args.k, title=f'Evaluating {type(self)}') as bar:
            for train, test in KFold(**k_fold_args).split(np_bench):
                self.train(benchmarks=np_bench[train])
                pred = self.predict(np_bench[test])
                for it, indx in enumerate(test):
                    ret[indx] = pred[it]
                bar()
        return ret

    def mk_tabular_data(self, benchmarks):
        X_out, Y_out = [], []
        for benchmark in benchmarks:
            X_out.append(benchmark.get_features())
            y = []
            for solver in benchmark.get_solvers():
                score = benchmark.get_score(solver) + 1
                if score > args.max_score:
                    score = 2 * args.max_score
                y.append(score)
            Y_out.append(y)
        return np.array(X_out), np.log(np.array(Y_out))

    def name_to_solver(self, names):
        if isinstance(names, str): 
            return self.db.get_solver(names)

        return [self.db.get_solver(name) for name in names]

    def score_softmin(self, data, negate = False):
        if isinstance(data, list):
            return [self.score_softmin(v) for v in data]
        elif isinstance(data, dict):
            denon = sum(np.exp(-v) for v in data.values())
            for key in data:
                data[key] = np.exp(-data[key]) / denon
            return data
        else: raise ValueError
        
    def score_softmax(self, data, negate = False):
        if isinstance(data, list):
            return [self.score_softmax(v) for v in data]
        elif isinstance(data, dict):
            denon = sum(np.exp(v) for v in data.values())
            for key in data:
                data[key] = np.exp(data[key]) / denon
            return data
        else: raise ValueError