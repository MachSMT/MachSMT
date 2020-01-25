from sklearn.model_selection import LeaveOneOut,KFold
from smtzilla.compute_features import get_features,get_check_sat,get_feature_names
import multiprocessing.dummy as mp
from progress.bar import Bar
from smtzilla.search import get_inst_path

import numpy as np
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import pdb,os,sys,random,pickle

WALL_TIMEOUT = 2400
TIMEOUT = 2398
USE_EXTRA_FEATURES=True ##NOT IMPLEMENTED
EXTRA_CAP=True
EXTRA_MAX=10000

num_cores = 12

class LearnedModel:
    def __init__(self,theory,track,db,model_maker):
        self.db = db
        self.model_maker = model_maker
        self.X = None
        self.Y = None
        self.extra_X = {}
        self.extra_Y = {}
        self.selections_core = None
        self.selections_div  = None
        self.selections = None
        self.solvers = None
        self.inputs = None
        self.random_selections = None
        self.theory = theory
        self.track = track
        self.solvers = None
        self.is_incr = track.lower().find('incremental') != -1 and track.lower().find('non-incremental') == -1
        self.greedy = False
        self.best_solver = None
        self.lm = {}
        self.scoring = {}
        self.use_core = None

    def get_score(self,solver,inst):

        if self.db[solver][inst]['result'].find('unknown') != -1:
            return 2.0 * WALL_TIMEOUT

        if not self.is_incr and self.db[solver][inst]['result'] != self.db[solver][inst]['expected']:
            if self.db[solver][inst]['expected'].lower().find('unknown') != -1:
                return float(self.db[solver][inst]['wallclock time'])
            elif  self.db[solver][inst]['result'].lower().find('unknown') >= 0:
                return 2.0 * WALL_TIMEOUT
            else:
                print("WRONG ANSWER!", solver, inst, self.theory, self.track, self.db[solver][inst]['result'] ,self.db[solver][inst]['expected'])
                return 10.0 * WALL_TIMEOUT
        elif self.is_incr:
            if int(self.db[solver][inst]['wrong-answers']) != 0:
                print("WRONG ANSWER!", solver, inst, self.theory, self.track)
                return 10.0 * WALL_TIMEOUT
            if get_check_sat(get_inst_path(self.theory,inst)) == int(self.db[solver][inst]['correct-answers']):
                if float(self.db[solver][inst]['wallclock time']) < TIMEOUT:
                    return float(self.db[solver][inst]['wallclock time'])
                else:
                    return 2.0 * WALL_TIMEOUT
            else:
                return 2.0 * WALL_TIMEOUT
        else:
            if float(self.db[solver][inst]['wallclock time']) < TIMEOUT:
                return float(self.db[solver][inst]['wallclock time'])
            else:
                return 2.0 * WALL_TIMEOUT
            return float(self.db[solver][inst]['wallclock time'])

    def calc_features(self,use_full_db,full_db):
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
        self.inputs = list(inputs)
        self.X = [ None for i in self.inputs]
        self.Y = [ None for i in self.inputs]
        bar = Bar('Computing Features for theory=' + self.theory + '\ttrack=' + self.track, max=len(inputs))

        def mp_call(index_instance):
            index = index_instance[0]
            instance = index_instance[1]
            self.X[index] = get_features(file_path=get_inst_path(self.theory,instance),theory=self.theory,track=self.track)
            times = []
            for solver in self.solvers:
                v = self.get_score(solver,instance) ##DO NOT NEED TO CHECK AGAINST TIMEOUT HERE
                times.append(np.log(max(0.001,v)))
            self.Y[index] = times
            bar.next()
        with mp.Pool(min(len(self.inputs),1)) as pool:
            pool.map(mp_call,list(enumerate(self.inputs)))
        bar.finish()

        if use_full_db:
            it=0
            logics = ['A', 'AX', 'BV', 'FP', 'I', 'UF', 'DL', 'UF']
            common = []
            for theory in full_db.db:
                for l in logics:
                    if self.theory.find(l) != -1 and theory.find(l) != -1 and self.theory != theory:
                        common.append(theory)
            print(common)
            bonus_inputs = {}
            for theory in common:
                for track in full_db.db[theory]:
                    for solver in full_db.db[theory][track]:
                        if solver in self.solvers:
                            if solver not in self.extra_X:
                                self.extra_X[solver] = []
                                self.extra_Y[solver] = []
                                bonus_inputs[solver] = []
                            for instance in full_db.db[theory][track][solver]:
                                self.extra_X[solver].append(None)
                                self.extra_Y[solver].append(None)
                                bonus_inputs[solver].append((instance,theory,track,solver))
                                it+=1

        if EXTRA_CAP:
            it=0
            for solver in self.solvers:
                if solver in bonus_inputs and len(bonus_inputs[solver]) > EXTRA_MAX:
                    random.shuffle(bonus_inputs[solver])
                    bonus_inputs[solver] = [bonus_inputs[solver][i] for i in range(EXTRA_MAX)]
                    self.extra_X[solver] = [None] * EXTRA_MAX
                    self.extra_Y[solver] = [None] * EXTRA_MAX
                    it += EXTRA_MAX
                else:
                    if solver not in bonus_inputs:
                        continue
                    it += len(bonus_inputs[solver])
                    
        
        bar = Bar('Computing Extra Features for Theory=' + self.theory + '\tTrack=' + self.track, max=it)

        def mp_call2(index_args):
            index = index_args[0]
            args = index_args[1]
            instance = args[0]
            theory = args[1]
            track = args[2]
            solver = args[3]
            bonus_input_par_X[index] = get_features(file_path=get_inst_path(theory,instance),theory=theory,track=track)
            bonus_input_par_Y[index] = np.log(max(0.001,full_db.compute_score(theory=theory,track=track,solver=solver,inst=instance)))
            bar.next()

        for solver in bonus_inputs:
            bonus_input_par_X = [None] * it
            bonus_input_par_Y = [None] * it
            with mp.Pool(min(len(bonus_inputs[solver]),num_cores)) as pool:
                pool.map(mp_call2,list(enumerate(bonus_inputs[solver])))
            self.extra_X[solver] = [v for v in bonus_input_par_X if v != None]
            self.extra_Y[solver] = [v for v in bonus_input_par_Y if v != None]
        bar.finish()

    def eval(self):
        self.X = np.array(self.X)
        self.Y = np.array(self.Y)
        self.log_score_predictions_core = []
        self.log_score_predictions_div  = []
        for i in range(len(self.X)):
            self.log_score_predictions_core.append([None for solver in self.solvers])
            self.log_score_predictions_div.append([None for solver in self.solvers])
        self.selections = [None for i in range(len(self.X))]
        self.random_selections = [None for i in range(len(self.X))]

        k = len(self.X)
        if k > 150:
            k = 10
        bar = Bar('Fitting Core -- theory=' + self.theory + '\ttrack=' + self.track, max=k)

        def mp_call(train_test_index):
            train_index = train_test_index[0]
            test_index = train_test_index[1]
            features_train, features_test = self.X[train_index], self.X[test_index]
            labels_train, labels_test = self.Y[train_index], self.Y[test_index]
            models = {}
            for i in range(len(self.solvers)):
                models[self.solvers[i]] = self.model_maker(n_points=len(self.X))
                models[self.solvers[i]].fit(features_train,labels_train[:,i])
                for j in range(len(test_index)):
                    self.log_score_predictions_core[test_index[j]][i] = models[self.solvers[i]].predict(features_test[j].reshape(1, -1))[0]
            bar.next()
        

        def mp_call2(train_test_index):
            train_index = train_test_index[0]
            test_index = train_test_index[1]
            features_train, features_test = self.X[train_index], self.X[test_index]
            labels_train, labels_test = self.Y[train_index], self.Y[test_index]
            models = {}
            for i in range(len(self.solvers)):
                X = features_train
                Y = labels_train[:,i]
                if self.solvers[i] in self.extra_X: 
                    X = np.append(X,np.array(self.extra_X[self.solvers[i]]),axis=0)
                    Y = np.append(Y,np.array(self.extra_Y[self.solvers[i]]))
                models[self.solvers[i]] = self.model_maker(n_points=len(self.X))
                models[self.solvers[i]].fit(X,Y)
                for j in range(len(test_index)):
                    self.log_score_predictions_div[test_index[j]][i] = models[self.solvers[i]].predict(features_test[j].reshape(1, -1))[0]
            bar.next()

        ##K FOLD CROSS VALIDATION
        with mp.Pool(min(len(self.X), 12)) as pool:
            pool.map(mp_call,KFold(n_splits=k, shuffle=True).split(self.X))
        bar.finish()

        bar = Bar('Fitting Div -- theory=' + self.theory + '\ttrack=' + self.track, max=k)

        with mp.Pool(min(len(self.X), 12)) as pool:
            pool.map(mp_call2,KFold(n_splits=k, shuffle=True).split(self.X))
        bar.finish()
        self.selections_core, self.selections_div = [None] * len(self.X), [None] * len(self.X)
        for i in range(len(self.X)):
            self.selections_core[i] = self.solvers[np.argmin(self.log_score_predictions_core[i])]
            self.selections_div[i]  = self.solvers[np.argmin(self.log_score_predictions_div[i])]
            self.random_selections[i] = np.random.choice(self.solvers)
        bar.finish()

    def build(self):
        c=0
        if self.use_core == False:
            self.X = np.append(self.X,np.array(self.extra_X[self.solvers[i]]),axis=0)
        for i  in range(len(self.solvers)):
            sY = self.Y[:,i]
            if self.use_core == False:
                sY = np.append(sY,np.array(self.extra_Y[self.solvers[i]]))
            self.lm[self.solvers[i]] = self.model_maker(len(self.X))
            self.lm[self.solvers[i]].fit(self.X,sY)

    def baseline(self):
        self.best_solver = None
        best_par2 = float('+inf')
        for solver in self.solvers:
            par2 = 0.0
            for inst in self.inputs:
                par2 += self.get_score(solver,inst)
            if par2 < best_par2:
                best_par2, self.best_solver = par2,solver
        my_par2_core, my_par2_div = 0.0 , 0.0
        for it in range(len(self.selections)):
            my_par2_core += self.get_score(solver=self.selections_core[it],inst=self.inputs[it])
            my_par2_div  += self.get_score(solver=self.selections_div[it],inst=self.inputs[it])
        if best_par2 < min(my_par2_core, my_par2_div):
            ##Failed to learn, force greedy solution
            print("Failed to improve, enabling Greedy Selection")
            self.selections = [self.best_solver for i in range(len(self.X))]
            self.greedy = True
        else:
            print("Observe CORE improvement of: " + str(round(100.0 * (best_par2 - my_par2_core) / my_par2_core)) + "%",flush=True)
            print("Observe DIV  improvement of: " + str(round(100.0 * (best_par2 - my_par2_div) / my_par2_div)) + "%",flush=True)
            if my_par2_core < my_par2_div:
                self.use_core = True
                self.selections = self.selections_core
            else:
                self.use_core = False
                self.selections = self.selections_div

    def mk_plots(self):
        plt.cla()
        plt.clf()
        plot_data = []
        
        if not os.path.exists('results'):
            os.mkdir('results')
        if not os.path.exists('results/'+self.theory):
            os.mkdir('results/' + self.theory)
        if not os.path.exists('results/' + self.theory +'/' + self.track.split('/')[-1] ):
            os.mkdir('results/' + self.theory +'/' + self.track.split('/')[-1])
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
        plot_data.append(('Random Selection', [self.get_score(solver=self.random_selections[it],inst=self.inputs[it]) for it in range(len(self.X))]))


        #SMTZILLA
        plot_data.append(('SMTZILLA', [self.get_score(solver=self.selections[it],inst=self.inputs[it]) for it in range(len(self.X))]))
        
        import itertools
        marker = itertools.cycle((',', '+', '.', 'o', '*')) 
        colors = itertools.cycle(('b','g','r','c','m','y')) 

        for d in plot_data:
            d[1].sort()
            if d[0] != 'SMTZILLA':
                plt.plot([v for v in d[1] if v < TIMEOUT], label=d[0],marker=next(marker),color=next(colors))
            else:
                plt.plot([v for v in d[1] if v < TIMEOUT], label=d[0],color='purple',marker='d')
            self.scoring[d[0]] = sum(d[1])

        plt.legend()
        plt.savefig('results/' + self.theory +'/' + self.track.split('/')[-1] + '/plot.png',dpi=700)
        plt.cla()
        plt.clf()

        pickle.dump(plot_data, open('results/'+self.theory + '/' + self.track.split('/')[-1] + '/plot_data.p' , "wb" ))


    def log(self):
        track = self.track
        if not os.path.exists('results'):
            os.mkdir('results')
        if not os.path.exists('results/'+self.theory):
            os.mkdir('results/' + self.theory)
        if not os.path.exists('results/' + self.theory +'/' + self.track.split('/')[-1] ):
            os.mkdir('results/' + self.theory +'/' + self.track.split('/')[-1])
        with open('results/' + self.theory +'/' + self.track.split('/')[-1] + '/selections.csv','w') as file:
            features = get_feature_names()
            file.write('instance,')
            for f in features:
                file.write(f + ',')
            file.write('selection\n')
            for it in range(len(self.X)):
                file.write(self.inputs[it] + ',')
                for v in self.X[it,]:
                    file.write(str(v) + ',')
                file.write(self.selections[it] + '\n')
        
        with open('results/' + self.theory + '/' + self.track.split('/')[-1] + '/par2.csv','w') as file:
            data = []
            for solver in self.scoring:
                data.append((solver,self.scoring[solver]))
            data.sort(key=lambda x:x[1])
            file.write('solver,score\n')
            for solver,par2 in data:
                file.write(solver + ',' + str(par2) + '\n')
            
    def predict(self, file):
        if self.greedy:
            return self.best_solver
        X = np.array(get_features(file_path=file,theory=self.theory,track=self.track))
        Y = []
        for solver in self.solvers:
            Y.append(self.lm[solver].predict(X.reshape(1, -1))[0])
        return self.solvers[np.argmin(Y)]

    def run(self,use_full_data=False,full_db=None):
        self.calc_features(use_full_data,full_db)
        if len(self.X) < 5:
            print("Not enough inputs to build model.")
            return
        self.eval()
        self.build()
        self.baseline()
        self.mk_plots()
        self.log()