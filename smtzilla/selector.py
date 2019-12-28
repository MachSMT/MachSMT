from sklearn.model_selection import LeaveOneOut,KFold
from smtzilla.compute_features import get_features,get_check_sat
import multiprocessing.dummy as mp
from progress.bar import Bar
from smtzilla.search import get_inst_path

import numpy as np
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import pdb

WALL_TIMEOUT = 2400
TIMEOUT = 2000

class LearnedModel:
    def __init__(self,theory,track,db,model_maker):
        self.db = db
        self.model_maker = model_maker
        self.X = None
        self.Y = None
        self.selections = None
        self.solvers = None
        self.random_selections = None
        self.theory = theory
        self.track = track
        self.solvers = None
        self.is_incr = track.lower().find('incremental') != -1 and track.lower().find('non-incremental') == -1
        self.greedy = False
        self.greedy_solver = None
        self.lm = {}

    def get_score(self,solver,inst):
        if not self.is_incr and self.db[solver][inst]['result'] != self.db[solver][inst]['expected']:
            if self.db[solver][inst]['expected'].lower().find('unknown') != -1:
                return float(self.db[solver][inst]['cpu time'])
            elif  self.db[solver][inst]['result'].lower().find('unknown'):
                return 2.0 * WALL_TIMEOUT
            else:
                print("WRONG ANSWER!", solver, inst, self.theory, self.track, self.db[solver][inst]['result'] ,self.db[solver][inst]['expected'])
                return 10.0 * WALL_TIMEOUT
        elif self.is_incr:
            if int(self.db[solver][inst]['wrong-answers']) != 0:
                print("WRONG ANSWER!", solver, inst, self.theory, self.track)
                return 10.0 * WALL_TIMEOUT
            if get_check_sat(get_inst_path(self.theory,inst)) == int(self.db[solver][inst]['correct-answers']):
                if float(self.db[solver][inst]['cpu time']) < TIMEOUT:
                    return float(self.db[solver][inst]['cpu time'])
                else:
                    return 2.0 * WALL_TIMEOUT
            else:
                return 2.0 * WALL_TIMEOUT
        else:
            if float(self.db[solver][inst]['cpu time']) < TIMEOUT:
                return float(self.db[solver][inst]['cpu time'])
            else:
                return 2.0 * WALL_TIMEOUT
            return float(self.db[solver][inst]['cpu time'])

    def calc_features(self):
        inputs = set()
        solvers = set()
        for solver in self.db:
            if solver.lower().find('par4') != -1:
                continue
            solvers.add(solver)
            for inst in self.db[solver]:
                inputs.add(inst)
        solvers = list(solvers)
        solvers.sort()
        self.solvers = solvers
        self.X = [ None for i in inputs ]
        self.Y = [ None for i in inputs ]
        bar = Bar('Computing Features for theory=' + self.theory + '\ttrack=' + self.track, max=len(inputs))


        def mp_call(index_instance):
            index = index_instance[0]
            instance = index_instance[1]
            self.X[index] = get_features(file_path=get_inst_path(self.theory,instance),theory=self.theory,track=self.track)
            times = []
            for solver in self.solvers:
                v = self.get_score(solver,instance)
                times.append(np.log(max(0.001,v)))
            self.Y[index] = times
            bar.next()

        with mp.Pool(min(len(inputs),12)) as pool:
            pool.map(mp_call,list(enumerate(inputs)))
        bar.finish()

    def eval(self):
        self.X = np.array(self.X)
        self.Y = np.array(self.Y)
        self.selections = np.zeros(len(self.X))
        self.random_selections = np.zeros(len(self.X))
        bar = Bar('Fitting theory=' + self.theory + '\ttrack=' + self.track, max=len(self.X))

        def mp_call(train_test_index):
            train_index = train_test_index[0]
            test_index = train_test_index[1]
            features_train, features_test = self.X[train_index], self.X[test_index]
            labels_train, labels_test = self.Y[train_index], self.Y[test_index]
            models = {}
            pred = []
            for i in range(len(self.solvers)):
                pca = len(self.X) > 10
                models[self.solvers[i]] = self.model_maker(pca)
                models[self.solvers[i]].fit(features_train,labels_train[:,i])
                pred.append(models[self.solvers[i]].predict(features_test))
            c=0
            for it in test_index:
                predictions = [pred[i][c] for i in range(len(self.solvers))]
                solver_index = np.argmin(predictions)
                self.selections[it] = np.exp(self.Y[it,solver_index])

                random_index = np.random.choice(len(self.solvers))
                self.random_selections[it] = np.exp(self.Y[it,random_index])
                bar.next()
        with mp.Pool(min(len(self.X), 12)) as pool:
            pool.map(mp_call,KFold(n_splits=min(10,len(self.X)),shuffle=True).split(self.X))
        for solver in self.solvers:
            pca = len(self.X) > 10
            self.lm[solver] = self.model_maker(pca)
            self.lm[solver].fit(self.X,self.Y)
        bar.finish()
        self.greedify()

    def greedify(self):
        best_solver = None
        best_par2 = float('+inf')
        for solver in self.solvers:
            par2 = 0.0
            for inst in self.db[solver]:
                par2 += self.get_score(solver,inst)
            if par2 < best_par2:
                best_par2, best_solver = par2,solver
        my_par2 = 0.0
        for v in self.selections:
            my_par2 += v
        if best_par2 < my_par2:
            print("GREEDY ACTIVE", self.theory, self.track)
            self.greedy = True
            self.greedy_solver = best_solver
            self.selections = [self.get_score(best_solver,inst) for inst in self.db[best_solver]]
        

    def mk_plots(self):
        plt.cla()
        plt.clf()

        plot_data = []
        
        #individual solvers
        for solver in self.solvers:
            rt = []
            for inst in self.db[solver]:
                rt.append(self.get_score(solver,inst))
            plot_data.append((solver,rt))
        
        #vb solver
        vb = []
        for inst in self.db[self.solvers[0]]:
            vb_rt = float('+inf')
            for solver in self.solvers:
                vb_rt = min(vb_rt, self.get_score(solver,inst))
            vb.append(vb_rt)
        plot_data.append(('Virtual Best', vb))

        #Random Solver
        plot_data.append(('Random Selection', self.random_selections))


        #SMTZILLA
        plot_data.append(('SMTZILLA', self.selections))
        
        logfile = open('par2_log.txt', 'a')
        import itertools
        marker = itertools.cycle((',', '+', '.', 'o', '*')) 
        colors = itertools.cycle(('b','g','r','c','m','y')) 

        for d in plot_data:
            d[1].sort()
            if d[0] != 'SMTZILLA':
                plt.plot([v for v in d[1] if v < TIMEOUT], label=d[0],marker=next(marker),color=next(colors))
            else:
                plt.plot([v for v in d[1] if v < TIMEOUT], label=d[0],color='purple',marker='d')
            par2 = sum(d[1])
            for v in d[1]:
                if v >= TIMEOUT:
                    par2 += WALL_TIMEOUT * 2.0
                else:
                    par2 += v
            print(self.theory, self.track,d[0], par2,file=logfile)

        plt.legend()
        plt.savefig('figs/' + self.theory + '_' +self.track.split('/')[-1] + '.png',dpi=700)
        plt.cla()
        plt.clf()

    def predict(self, file):
        if self.greedy:
            return self.greedy_solver
        X = get_features(file_path=file,theory=self.theory,track=self.track)
        Y = []
        for solver in self.solvers:
            Y.append(self.lm[solver].predict(X))
        return self.solvers[np.argmin(Y)]