from .predictor import Predictor
from sklearn.model_selection import LeaveOneOut,KFold
from ..parser import args as settings
from ..db import database as db
import random,pdb

class Greedy(Predictor):
    def __init__(self,*args,**kwargs):
         super().__init__(*args,**kwargs)

    def eval(self,benchmarks):
        predictions = {}

        for track in db.get_tracks():
            for logic in db.get_logics(track=track):
                scores = dict((solver,0.0) for solver in db.get_solvers(logic=logic, track=track))
                benchmarks = sorted(db.get_benchmarks(logic=logic, track=track))
                solvers    = sorted(db.get_solvers(logic=logic, track=track))
                for train,test in KFold(n_splits=min(len(benchmarks),settings.k)).split(benchmarks):
                    ##Train
                    for solver in solvers:
                        scores[solver] = 0
                        for it,indx in enumerate(train):
                            if db[solver,benchmarks[indx]] == None:
                                scores[solver] = settings.timeout * 2 # not sure how to handle this....
                            else:
                                scores[solver] += db[solver,benchmarks[indx]]
                        sum([db[solver,benchmarks[indx]]  for it,indx in enumerate(train)])
                    ##Test
                    for it,indx in enumerate(test):
                        predictions[benchmark[it]] = {}
                        for solver in solvers:
                            predictions[benchmark[it]][solver] = scores[solver]
        return predictions

    def build(self,benchmarks):
        raise NotImplementedError

    def predict(self,benchmarks):
        raise NotImplementedError
