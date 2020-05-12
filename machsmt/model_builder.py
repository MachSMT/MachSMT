import pdb,os,sys,random,pickle,os
import numpy as np
from machsmt.model_maker import mk_regressor
import machsmt.settings as settings
from machsmt.util import die,warning

class ModelBuilder:
    def __init__(self,db):
        self.db = db
        self.structure = {}

    def organize(self):
        if not os.path.exists(settings.LIB_DIR): os.mkdir(settings.LIB_DIR)
        if not os.path.exists(settings.LIB_DIR + '/solvers'): os.mkdir(settings.LIB_DIR + '/solvers')
        if not os.path.exists(settings.LIB_DIR + '/tracks'): os.mkdir(settings.LIB_DIR + '/tracks')

        for solver in self.db.get_solvers():
            for benchmark in self.db.get_benchmarks(solver):
                if self.db[benchmark].logic not in self.structure: self.structure[self.db[benchmark].logic] = {}
                if self.db[benchmark].track not in self.structure[self.db[benchmark].logic]: self.structure[self.db[benchmark].logic][self.db[benchmark].track] = []
                logic, track = self.db[benchmark].logic, self.db[benchmark].track
                if solver not in self.structure[logic][track]: self.structure[logic][track].append(solver)

        for logic in self.structure:
            if not os.path.exists(settings.LIB_DIR + '/tracks/' + logic): os.mkdir(settings.LIB_DIR + '/tracks/' + logic)
            for track in self.structure[logic]:
                if not os.path.exists(settings.LIB_DIR + '/tracks/' + logic + '/' + track): 
                    os.mkdir(settings.LIB_DIR + '/tracks/' + logic + '/' + track)

    def build_solver_ehms(self):
        for solver in self.db.get_solvers():
            X, Y = [],[]
            for benchmark in self.db.get_benchmarks(solver):
                X.append(self.db[benchmark].get_features())
                Y.append(self.db[solver,benchmark])
            if not (len(X) > 5 and len(X[0]) > 0):
                warning("Not enough data to build EHM.",solver)
                continue
            with open(settings.LIB_DIR + '/solvers/' + solver + '.p', 'wb') as outfile:
                pickle.dump(mk_regressor(n_samples = len(X), n_features = len(X[0])).fit(X,Y), outfile)

    def build_track_ehms(self):
        for logic in self.structure:
            for track in self.structure[logic]:
                for solver in self.structure[logic][track]:
                    X, Y = [],[]
                    for benchmark in self.db.get_benchmarks(solver):
                        if self.db[benchmark].logic == logic and self.db[benchmark].track == track:
                            X.append(self.db[benchmark].get_features())
                            Y.append(self.db[solver,benchmark])
                    if not (len(X) > 5 and len(X[0]) > 0):
                        warning("Not enough data to build EHM.",solver,logic,track)
                        continue
                    with open(settings.LIB_DIR + '/tracks/' + logic + '/' + track + '/' + solver + '.p', 'wb') as outfile:
                        pickle.dump(mk_regressor(n_samples = len(X), n_features = len(X[0])).fit(X,Y), outfile)

    def build(self):
        self.organize()
        self.build_solver_ehms()
        self.build_track_ehms()