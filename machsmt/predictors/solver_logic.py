from .predictor import Predictor
from sklearn.model_selection import LeaveOneOut,KFold
from ..parser import args as settings
from ..db import database as db
from ..ml import mk_model
import random,pdb
import numpy as np
from progress.bar import Bar
from ..util import warning

class SolverLogic(Predictor):
    def __init__(self,*args,**kwargs):
         super().__init__(*args,**kwargs)
         self.lm = {}

    def eval(self):
        predictions = {}
        N = 0
        for solver in db.get_solvers():                 ##This calculation is incorrect
            for logic in db.get_logics(solver=solver):  ##But I'm not sure why
                N += 1                                  ##2020 sq returns 327 but only 61
        bar = Bar('Building Solver/Logic EHMs', max=N)
        for solver in db.get_solvers():
            logics = set(db.get_logics(solver=solver))
            if settings.logics:
                logics = logics.intersection(set(settings.logics))
            for logic in logics:
                X, Y = [],[]
                benchmarks = list(db.get_benchmarks(solver=solver,logic=logic))
                for benchmark in benchmarks:
                    X.append(db[benchmark].get_features())
                    Y.append(db[solver,benchmark])
                    if benchmark not in predictions: predictions[benchmark] = {}
                if len(X) < settings.min_datapoints:
                    warning("Not enough data to evaluate. " +str(len(X)) +'/' + str(settings.min_datapoints),solver,logic)
                    bar.next()
                    continue
                X,Y = np.array(X), np.log(np.array(Y)+1.0)
                for train, test in KFold(n_splits=settings.k,shuffle=True,random_state=settings.rng).split(X):
                    raw_predictions = mk_model(n_samples = len(X[train])).fit(X[train],Y[train]).predict(X[test])
                    for it, indx in enumerate(test):
                        predictions[benchmarks[indx]][solver] = np.exp(raw_predictions[it]) - 1.0
            bar.next()
        bar.finish()

        # assert len(predictions) == len(db)
        return predictions

    def build(self):
        for solver in db.get_solvers():
            logics = set(db.get_logics(solver=solver))
            if settings.logics:
                logics = logics.intersection(set(settings.logics))
            for logic in logics:
                if logic not in self.lm: self.lm[logic] = {}
                X, Y = [],[]
                benchmarks = list(db.get_benchmarks(solver=solver,logic=logic))
                for benchmark in benchmarks:
                    X.append(db[benchmark].get_features())
                    Y.append(db[solver,benchmark])
                if len(X) < settings.min_datapoints:
                    warning("Not enough data to evaluate. " +str(len(X)) +'/' + str(settings.min_datapoints),solver,logic)
                    continue
                X,Y = np.array(X), np.log(np.array(Y)+1.0)
                self.lm[logic][solver] = mk_model(n_samples = len(X)).fit(X,Y)

    def predict(self,benchmark):
        X = np.array(benchmark.get_features()).reshape(1, -1)
        logic = benchmark.get_logic()
        predictions = []
        if logic not in self.lm:
            raise ValueError("Not enough training data to make prediction.")
        for solver in self.lm[logic]:
            predictions.append((solver,self.lm[logic][solver].predict(X)))
        predictions.sort(key=lambda p:p[1])
        for solver,score in predictions:
            print(solver)