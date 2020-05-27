from .predictor import Predictor
from sklearn.model_selection import LeaveOneOut,KFold
from ..parser import args as settings
from ..util import warning
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
                if len(benchmarks) == 1:
                    predictions[benchmarks[0]] = random.choice(sorted(db.get_solvers(benchmarks[0])))
                    continue
                for train,test in KFold(n_splits=min(len(benchmarks),settings.k)).split(benchmarks):
                    ##Train
                    for solver in solvers:
                        scores[solver] = 0
                        n=0
                        for it,indx in enumerate(train):
                            try:
                                scores[solver] += db[solver,benchmarks[indx]]
                                n += 1
                            except:
                                pass
                        if n == 0:
                            scores[solver] = float('inf')
                        else:
                            scores[solver] /= n
                    ##Test
                    for it,indx in enumerate(test):
                        predictions[benchmarks[indx]] = {}
                        for solver in db.get_solvers(benchmarks[indx]):
                            predictions[benchmarks[indx]][solver] = scores[solver]
        it = 0
        for benchmark in db.get_benchmarks():
            if benchmark not in predictions:
                # warning("GREEDY failed prediction for: ", solver, benchmark)
                it += 1
                predictions[benchmark] = {}
                for solver in db.get_solvers(benchmark=benchmark):
                    if db[solver,benchmark] != None:
                        predictions[benchmark][solver] = random.random() # set prediction in hacky way
                assert len(predictions[benchmark]) > 0
        warning("Lost", it, "predictions")
        return predictions

    def build(self,benchmarks):
        raise NotImplementedError

    def predict(self,benchmarks):
        raise NotImplementedError
