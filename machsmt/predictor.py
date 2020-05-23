import pdb,os,sys,random,pickle,os,glob,itertools
import numpy as np
from machsmt.model_maker import mk_model
import machsmt.settings as settings
from machsmt.util import die,warning
from machsmt.benchmark import Benchmark
from sklearn.model_selection import LeaveOneOut,KFold
from sklearn.preprocessing import OneHotEncoder
from progress.bar import Bar
from machsmt.smtlib import logic_list,get_theories
import matplotlib.pyplot as plt
import multiprocessing.dummy as mp

class Predictor:
    def __init__(self,db,common=False):
        self.db = db
        self.predictions = {}
        self.runtime_predictions = {}
        self.classifications = {}
        self.common = common
        for benchmark in self.db.get_benchmarks(): 
            self.runtime_predictions[benchmark] = {}
            self.classifications[benchmark] = {}
        
    def one_hot(self,solver):
        s = sorted(self.db.get_solvers())
        ret = [0] * len(s)
        ret[s.index(solver)] = 1
        return ret

    def eval(self):
        raise NotImplementedError
    def build(self):
        raise NotImplementedError

class RandomSelector(Predictor):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def eval(self,logic=None):
        for benchmark in self.db.get_benchmarks():
            self.predictions[benchmark] = random.choice(self.db.get_solvers(benchmark))

class SolverPredictor(Predictor):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def eval(self,logic=None):
        bar = Bar('Building Solver EHMs', max=len(list(self.db.get_solvers())))
        for solver in self.db.get_solvers():
            X, Y = [],[]
            benchmarks = list(self.db.get_benchmarks(solver))
            for benchmark in benchmarks:
                X.append(self.db[benchmark].get_features())
                Y.append(self.db[solver,benchmark])
                if benchmark not in self.runtime_predictions: self.runtime_predictions[benchmark] = {}
            if len(X) < settings.MIN_DATA_POINTS:
                warning("Not enough data to evaluate. " +str(len(X)) +'/' + str(settings.MIN_DATA_POINTS),solver,logic)
                bar.next()
                continue
            X,Y = np.array(X), np.log(np.array(Y)+1.0)
            for train, test in KFold(n_splits=settings.K_FOLD,shuffle=True).split(X):
                raw_predictions = mk_model(n_samples = len(X[train])).fit(X[train],Y[train]).predict(X[test])
                for it, indx in enumerate(test):
                    self.runtime_predictions[benchmarks[indx]][solver] = np.exp(raw_predictions[it]) - 1.0
            bar.next()
        bar.finish()
        print("Gathering Predictions")
        for benchmark in self.db.get_benchmarks():
            best,ptime = None, float('+inf')
            for solver in self.runtime_predictions[benchmark]:
                if self.runtime_predictions[benchmark][solver] < ptime: best,ptime = solver, self.runtime_predictions[benchmark][solver]
            self.predictions[benchmark] = self.db[best,benchmark]
        
class TrackPredictor(Predictor):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class LogicPredictor(Predictor):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class LogicTrackPredictor(Predictor):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def eval(self,logics=None):
        N = 0
        args = []
        mutex = mp.Lock()
        for logic in (self.db.get_logics() if logics == None else logics):
            for track in self.db.get_tracks(logic):
                for solver in self.db.get_solvers(logic=logic,track=track):
                    N += 1
                    args.append((logic,track,solver))
        bar = Bar('Building Track EHMs', max=N)
        def mp_call(arg):
            logic,track,solver=arg
            X, Y = [],[]
            X_xtra, Y_xtra = [], []
            all_benchmarks = list(self.db.get_benchmarks(solver))
            benchmarks = []
            for benchmark in all_benchmarks:
                try:
                    if self.db[benchmark].logic == logic and self.db[benchmark].track == track:
                        X.append(self.db[benchmark].get_features())
                        Y.append(self.db[solver,benchmark])
                        benchmarks.append(benchmark)
                    elif self.common and len(set(get_theories(self.db[benchmark].logic)).intersection(get_theories(self.db[benchmark].logic))) > 0:
                        X_xtra.append(self.db[benchmark].get_features())
                        Y_xtra.append(self.db[solver,benchmark])
                except:
                    warning("Weird rare crash." , logic, track,solver)
                    return
            if len(X) < settings.MIN_DATA_POINTS:
                warning("Not enough data to evaluate. " +str(len(X)) +'/' + str(settings.MIN_DATA_POINTS),solver,logic,track)
                bar.next()
                return
            ##
            X,Y = np.array(X), np.log(np.array(Y)+1)
            for train, test in KFold(n_splits=settings.K_FOLD,shuffle=True).split(X):
                raw_predictions = mk_model(n_samples = len(X[train])).fit(
                                    np.concatenate((X[train],X_xtra)),
                                    np.concatenate((Y[train],Y_xtra)),
                ).predict(X[test]) if self.common else \
                                mk_model(n_samples = len(X[train])).fit(
                                    X[train],
                                    Y[train],
                ).predict(X[test])
                for it, indx in enumerate(test):
                    self.runtime_predictions[benchmarks[indx]][solver] = np.exp(raw_predictions[it]) - 1.0
            mutex.acquire()
            bar.next()
            mutex.release()
        
        with mp.Pool(settings.CORES) as pool:
            pool.map(mp_call,args)
        print("Gathering Predictions")
        for benchmark in self.db.get_benchmarks():
            best,ptime = None, float('+inf')
            for solver in self.runtime_predictions[benchmark]:
                if self.runtime_predictions[benchmark][solver] < ptime: best,ptime = solver, self.runtime_predictions[benchmark][solver]
            if best == None:
                best = random.choice(self.db.get_solvers(benchmark))
                warning("No prediction for: ", benchmark,self.db[benchmark].logic,self.db[benchmark].track)
            self.predictions[benchmark] = self.db[best,benchmark]
        bar.finish()
        
class PairwisePredictor(Predictor):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def eval(self,logics):
        # for benchmark in self.db.get_benchmarks(): 
        #     self.runtime_predictions[benchmark] = {}
        #     self.classifications[benchmark] = {}
        N = len(sorted(self.db.get_solvers()))
        N = N * (N-1) / 2
        bar = Bar('Building Pairwise Model', max=N)
        for solver1 in sorted(self.db.get_solvers()):
            for solver2 in sorted(self.db.get_solvers()):
                if solver1 >= solver2: 
                    bar.next()
                    continue
                X,Y = [], []
                bench1 = set(self.db.get_benchmarks(solver1))
                bench2= set(self.db.get_benchmarks(solver2))
                common_benchmarks = sorted(bench1.intersection(bench2))
                if len(common_benchmarks) == 0: break 
                for bench in common_benchmarks:
                    pass
                for bench in common_benchmarks:
                    X.append(self.db[bench].get_features())
                    Y.append(1 if self.db[solver1,bench] < self.db[solver2,bench] else 0)
                if len(X) < settings.MIN_DATA_POINTS:
                    warning("Not enough data to evaluate. " +str(len(X)) +'/' + str(settings.MIN_DATA_POINTS),solver1,solver2)
                    bar.next()
                    continue
                X,Y = np.array(X), np.array(Y)
                
                for train, test in KFold(n_splits=settings.K_FOLD,shuffle=True).split(X):
                    predictions = mk_model(n_samples = len(X[train]),classifier=True).fit(
                        X[train],Y[train]
                    ).predict(X[test])
                    for it, indx in enumerate(test):
                        self.classifications[common_benchmarks[indx]][(solver1,solver2)] = predictions[it]
                bar.next()
        bar.finish()
        print("Collecting Results")
        for benchmark in self.db.get_benchmarks():
            if benchmark not in self.classifications:
                self.predictions[benchmark] = random.choice(self.db.get_solvers(benchmark))
            scores = dict((s,0) for s in sorted(self.db.get_solvers(benchmark)))
            for solver1 in sorted(self.db.get_solvers()):
                for solver2 in sorted(self.db.get_solvers()):
                    if solver1 >= solver2: continue
                    if (solver1,solver2) not in self.classifications[benchmark]: continue
                    if self.classifications[benchmark][(solver1,solver2)] == 1: scores[solver1] += 1
                    else: scores[solver1] += 1
            self.predictions[benchmark] = self.db[max(scores,key=lambda v:v[1]),benchmark]