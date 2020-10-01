from ..db import database as db
from ..util import MachSMTException
class Predictor:
    def __init__(self):
        if len(db) == 0: raise MachSMTException("Empty Database.")
        
    # def ehm_runner(self,X,Y):
    #     X,Y = np.array(X), np.log(np.array(Y)+1.0)
    #     for train, test in KFold(n_splits=settings.k).split(X):
    #         raw_predictions = mk_model(n_samples = len(X[train])).fit(X[train],Y[train]).predict(X[test])
    #         for it, indx in enumerate(test):
    #             predictions[benchmarks[indx]][solver] = np.exp(raw_predictions[it]) - 1.0
