from .predictor import Predictor
from sklearn.model_selection import LeaveOneOut,KFold
from ..parser import args as settings
from ..db import database as db
from ..ml import mk_model
import random,pdb
import numpy as np
from progress.bar import Bar
from ..util import warning

class PairWise(Predictor):
    def __init__(self,*args,**kwargs):
         super().__init__(*args,**kwargs)

    def eval(self):
        N = 0
        predictions,classifications = {},{}
        for solver1 in sorted(db.get_solvers()):
            for solver2 in sorted(db.get_solvers()):
                if solver1 >= solver2: continue
                N+=1
        bar = Bar('Building Pairwise Model', max=N)
        for solver1 in sorted(db.get_solvers()):
            for solver2 in sorted(db.get_solvers()):
                X,Y = [], []
                if solver1 >= solver2: continue
                bench1, bench2 = set(db.get_benchmarks(solver1)), set(db.get_benchmarks(solver2))
                common_benchmarks = sorted(bench1.intersection(bench2))
                for benchmark in common_benchmarks:
                    X.append(db[benchmark].get_features())
                    Y.append(1 if db[solver1,benchmark] < db[solver2,benchmark] else 0)
                    if benchmark not in predictions: 
                        predictions[benchmark] = {}
                        classifications[benchmark] = {}
                if len(X) < settings.min_datapoints:
                    warning("Not enough data to evaluate. " +str(len(X)) +'/' + str(settings.min_datapoints),solver1,solver2)
                    bar.next()
                    continue
                X,Y = np.array(X), np.array(Y)
                for train, test in KFold(n_splits=settings.k,shuffle=True,random_state=settings.rng).split(X):
                    raw_predict = mk_model(n_samples = len(X[train]),classifier=True).fit(
                        X[train],Y[train]
                    ).predict(X[test])
                    for it, indx in enumerate(test):
                        classifications[common_benchmarks[indx]][(solver1,solver2)] = raw_predict[it]
                bar.next()
        for benchmark in db.get_benchmarks():
            if benchmark not in classifications: continue
            scores = dict((s,0) for s in sorted(db.get_solvers(benchmark)))
            for solver1 in sorted(db.get_solvers(benchmark)):
                for solver2 in sorted(db.get_solvers(benchmark)):
                    if solver1 >= solver2: continue
                    if (solver1,solver2) not in classifications: continue
                    if classifications[benchmark][(solver1,solver2)] == 1: scores[solver1] += 1
                    else: scores[solver2] += 1
            best = max(scores,key=lambda v:scores[v])
            predictions[benchmark][best] = -100000 # this sets the prediction... will clean up later... its late :)
        return predictions

    def build(self,benchmarks):
        raise NotImplementedError

    def predict(self,benchmarks):
        raise NotImplementedError