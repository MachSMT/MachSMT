from .predictor import Predictor
from sklearn.model_selection import LeaveOneOut,KFold
from ..parser import args as settings
from ..util import warning
from ..db import database as db
import random,pdb

class Greedy(Predictor):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)     
        self.scores = None
    def eval(self):
        predictions = {} #returned data structure 
                         #benchmark x solver x  predicted time
        for track in db.get_tracks():
            logics = set(db.get_logics(track=track))
            if settings.logics:
                logics.intersection(set(settings.logics))
            for logic in logics:
                scores = dict((solver,0.0) for solver in db.get_solvers(logic=logic, track=track))
                benchmarks = sorted(db.get_benchmarks(logic=logic, track=track))
                solvers    = sorted(db.get_solvers(logic=logic, track=track))
                if len(benchmarks) == 1:
                    predictions[benchmarks[0]] = {}
                    for solver in solvers:
                        predictions[benchmarks[0]][solver] = random.random() * settings.timeout
                    continue
                for train,test in KFold(n_splits=min(len(benchmarks),settings.k),shuffle=True,random_state=settings.rng).split(benchmarks):
                    ##Train
                    for solver in solvers:
                        scores[solver] = 0
                        n=0
                        for it,indx in enumerate(train):
                            try:
                                scores[solver] += db[solver,benchmarks[indx]]
                                n += 1
                            except IndexError:  ## No data for this solver/benchmarkspair 
                                pass            ##(expected sometimes on incomplete data.
                        if n == 0:
                            scores[solver] = float('inf')
                        else:
                            scores[solver] /= n
                    ##Test
                    for it,indx in enumerate(test):
                        predictions[benchmarks[indx]] = {}
                        for solver in db.get_solvers(benchmarks[indx]):
                            predictions[benchmarks[indx]][solver] = scores[solver]
        assert len(predictions) == len(db)
        return predictions

    def build(self):
        self.scores = {}
        for track in db.get_tracks():
            self.scores[track] = {}
            for logic in db.get_logics(track=track):
                self.scores[track][logic] = {}
                for solver in db.get_solvers(track=track,logic=logic):
                    self.scores[track][logic][solver], it = 0, 0
                    for benchmark in db.get_benchmarks(solver=solver,logic=logic,track=track):
                        self.scores[track][logic][solver] += db[solver,benchmark]
                        it += 1
                    if it > 0: self.scores[track][logic][solver] /= it 
                    else:      self.scores[track][logic][solver] = float('inf')

    def predict(self,benchmarks):
        ret = []
        for benchmark in benchmarks:
            logic, track = benchmark.get_logic(), benchmark.get_track()
            ret.append(min(self.scores[track][logic],key=self.scores[track][logic].get))