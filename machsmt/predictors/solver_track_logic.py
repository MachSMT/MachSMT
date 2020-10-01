from .predictor import Predictor
from sklearn.model_selection import LeaveOneOut,KFold
from ..parser import args as settings
from ..db import database as db
from ..ml import mk_model
import random,pdb
import numpy as np
from progress.bar import Bar
from ..util import warning

class SolverTrackLogic(Predictor):
    def __init__(self,*args,**kwargs):
         super().__init__(*args,**kwargs)

    def eval(self,benchmarks):
        bar = Bar('Building Solver/Track/Logic EHMs', max=len(list(db.get_solvers())))
        predictions = {}
        N = 0
        for solver in db.get_solvers():
            for track in db.get_tracks(solver=solver):
                for logic in db.get_logics(solver,track):
                    N += 1
        bar = Bar('Building Solver EHMs', max=N)
        for solver in db.get_solvers():
            for track in db.get_tracks(solver=solver):
                for logic in db.get_logics(solver=solver,track=track):
                    X, Y = [],[]
                    bench = list(db.get_benchmarks(solver=solver,logic=logic,track=track))
                    for benchmark in benchmarks:
                        X.append(db[benchmark].get_features())
                        Y.append(db[solver,benchmark])
                        if benchmark not in predictions: predictions[benchmark] = {}
                    if len(X) < settings.min_dp:
                        warning("Not enough data to evaluate. " +str(len(X)) +'/' + str(settings.min_dp),solver,track,logic)
                        bar.next()
                        continue
                    X,Y = np.array(X), np.log(np.array(Y)+1.0)
                    for train, test in KFold(n_splits=settings.k).split(X):
                        raw_predictions = mk_model(n_samples = len(X[train])).fit(X[train],Y[train]).predict(X[test])
                        for it, indx in enumerate(test):
                            predictions[benchmarks[indx]][solver] = np.exp(raw_predictions[it]) - 1.0
                    bar.next()
        bar.finish()
        assert len(predictions) == len(db)
        return predictions

    def build(self,benchmarks):
        raise NotImplementedError

    def predict(self,benchmarks):
        raise NotImplementedError
