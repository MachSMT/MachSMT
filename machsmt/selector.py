from sklearn.model_selection import LeaveOneOut,KFold
from machsmt.compute_features import get_features,get_check_sat,get_feature_names
import multiprocessing.dummy as mp ##?? other doesn't work for whatever reason...
from progress.bar import Bar
from machsmt.search import get_inst_path
from machsmt.db import get_db
import machsmt.settings as settings

import numpy as np
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import pdb,os,sys,random,pickle

import multiprocessing 
num_cores = multiprocessing.cpu_count()

class LearnedModel:
    def __init__(self,logic,track,db,model_maker):
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
        self.logic = logic
        self.track = track
        self.solvers = None
        self.is_incr = track.lower().find('incremental') != -1 and track.lower().find('non-incremental') == -1
        self.best_solver = None
        self.lm = {}
        self.scoring = {}
        self.use_core = None


    ## Computes features 

    def calc_features(self,):
        inputs = set()
        solvers = set()
        for solver in self.db:
            if solver.lower().find('par4') != -1:
                continue
            solvers.add(solver)
            for inst in self.db[solver]:
                inputs.add(inst)
        full_db = get_db()
        solvers = list(solvers)
        solvers.sort()
        self.solvers = solvers
        self.inputs = list(inputs)
        self.X = [ None for i in self.inputs]
        self.Y = [ None for i in self.inputs]
        bar = Bar('Computing Features for logic=' + self.logic + '\ttrack=' + self.track, max=len(inputs))


        mutex = mp.Lock()
        mutex2= mp.Lock()

        def mp_call(index_instance):
            index = index_instance[0]
            instance = index_instance[1]
            self.X[index] = get_features(file_path=get_inst_path(self.logic,instance),logic=self.logic,track=self.track)
            times = []
            for solver in self.solvers:
                v = full_db.compute_score(logic=self.logic,track=self.track,solver=solver,inst=instance)
                times.append(np.log(max(0.001,v)))
            self.Y[index] = times
            mutex.acquire()
            bar.next()
            mutex.release()
        with mp.Pool(min(len(self.inputs),num_cores)) as pool:
            pool.map(mp_call,list(enumerate(self.inputs)))
        bar.finish()

        ## COMPUTE MOST SIMILAR LOGICS
        it=0
        logics = ['A', 'AX', 'BV', 'FP', 'NIA', 'LIA', 'NRA', 'LRA' 'UF', 'DL', 'UF', 'QF']
        common = []
        for logic in full_db.db:
            for l in logics:
                if l and 'A':
                    if (l in self.logic[:-1]) and (l in logic[:-1]) and self.logic != logic:
                        common.append(logic)
                elif (l in self.logic) and (l in logic) and self.logic != logic:
                    common.append(logic)
        
        def diff(logic):
            #pdb.set_trace()
            ret = 0
            for l in logics:
                if l == 'A':
                    if (l in self.logic[:-1]) and (l in logic[:-1]): 
                        ret += 1
                elif (l in self.logic) and (l in logic): 
                    ret += 1
            return ret
        if settings.EXTRA_MAX == 0:
            return
        common.sort(key=diff)
        print([(t,diff(t)) for t in common])
        bonus_inputs = {}
        for logic in common:
            for track in full_db.db[logic]:
                for solver in full_db.db[logic][track]:
                    sit = 0
                    if solver in self.solvers:
                        if solver not in self.extra_X:
                            self.extra_X[solver] = []
                            self.extra_Y[solver] = []
                            bonus_inputs[solver] = []
                        for instance in full_db.db[logic][track][solver]:
                            self.extra_X[solver].append(None)
                            self.extra_Y[solver].append(None)
                            bonus_inputs[solver].append((instance,logic,track,solver))
                            it+=1
                            sit+=1
                            if sit > settings.EXTRA_MAX: break


        it=0
        for solver in self.solvers:
            if solver in bonus_inputs and len(bonus_inputs[solver]) > settings.EXTRA_MAX:
                random.shuffle(bonus_inputs[solver])
                bonus_inputs[solver] = [bonus_inputs[solver][i] for i in range(settings.EXTRA_MAX)]
                self.extra_X[solver] = [None] * settings.EXTRA_MAX
                self.extra_Y[solver] = [None] * settings.EXTRA_MAX
                it += settings.EXTRA_MAX
            else:
                if solver not in bonus_inputs:
                    continue
                it += len(bonus_inputs[solver])
                    
        
        bar = Bar('Computing Extra Features for logic=' + self.logic + '\tTrack=' + self.track, max=it)

        def mp_call2(index_args):
            index = index_args[0]
            args = index_args[1]
            instance = args[0]
            logic = args[1]
            track = args[2]
            solver = args[3]
            bonus_input_par_X[index] = get_features(file_path=get_inst_path(logic,instance),logic=logic,track=track)
            bonus_input_par_Y[index] = np.log(max(0.001,full_db.compute_score(logic=logic,track=track,solver=solver,inst=instance)))
            
            mutex2.acquire()
            bar.next()
            mutex2.release()

        for solver in bonus_inputs:
            bonus_input_par_X = [None] * it
            bonus_input_par_Y = [None] * it
            with mp.Pool(min(len(bonus_inputs[solver]),num_cores)) as pool:
                pool.map(mp_call2,list(enumerate(bonus_inputs[solver])))
            self.extra_X[solver] = [v for v in bonus_input_par_X if v != None]
            self.extra_Y[solver] = [v for v in bonus_input_par_Y if v != None]
        bar.finish()


    ## Main evaluation tool
    ## This is where we get our results from, deployment comes later
    ## Builds do types of EHM
    ## 1) Just over the track                   //in code this is refered to as 'core' (sorry for bad names)
    ## 2) Over track + cross over theories      //in code this is refered to as 'div' 
    ## Pick best one by score

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
        if k > 5:
            k = 5
        bar = Bar('Fitting Core -- logic=' + self.logic + '\ttrack=' + self.track, max=k)
        mutex = mp.Lock()
        mutex2= mp.Lock()
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
            mutex.acquire()
            bar.next()
            mutex.release()
        

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
            mutex2.acquire()
            bar.next()
            mutex2.release()

        ##K FOLD CROSS VALIDATION
        with mp.Pool(min(len(self.X), num_cores)) as pool:
            pool.map(mp_call,KFold(n_splits=k, shuffle=True).split(self.X))
        bar.finish()

        bar = Bar('Fitting Div -- logic=' + self.logic + '\ttrack=' + self.track, max=k)

        with mp.Pool(min(len(self.X), num_cores)) as pool:
            pool.map(mp_call2,KFold(n_splits=k, shuffle=True).split(self.X))
        bar.finish()
        self.selections_core, self.selections_div = [None] * len(self.X), [None] * len(self.X)
        for i in range(len(self.X)):
            self.selections_core[i] = self.solvers[np.argmin(self.log_score_predictions_core[i])]
            self.selections_div[i]  = self.solvers[np.argmin(self.log_score_predictions_div[i])]
            self.random_selections[i] = np.random.choice(self.solvers)
        bar.finish()


    ## Build deployment model
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


    ## Computes performance between 'core' and 'div'
    ## 
    def baseline(self):
        self.best_solver = None
        full_db = get_db()
        best_par2 = float('+inf')
        for solver in self.solvers:
            par2 = 0.0
            for inst in self.inputs:
                par2 += full_db.compute_score(logic=self.logic, track=self.track, solver=solver, inst=inst)
            if par2 < best_par2:
                best_par2, self.best_solver = par2,solver
        my_par2_core, my_par2_div = 0.0 , 0.0
        for it in range(len(self.selections)):
            my_par2_core += full_db.compute_score(logic=self.logic, track=self.track, solver=self.selections_core[it], inst=self.inputs[it])
            my_par2_div  += full_db.compute_score(logic=self.logic, track=self.track, solver=self.selections_div[it], inst=self.inputs[it])
        if best_par2 < min(my_par2_core, my_par2_div):
            ##Failed to learn, force greedy solution
            print("Failed to improve, enabling Greedy Selection")
            #self.selections = [self.best_solver for i in range(len(self.X))]
        else:
            print("Observe CORE improvement of: " + str(round(100.0 * (best_par2 - my_par2_core) / my_par2_core)) + "%",flush=True)
            print("Observe DIV  improvement of: " + str(round(100.0 * (best_par2 - my_par2_div) / my_par2_div)) + "%",flush=True)
            if my_par2_core < my_par2_div:
                self.use_core = True
                self.selections = self.selections_core
            else:
                self.use_core = False
                self.selections = self.selections_div


    def get_results_path(self):
        dirs = [settings.RESULTS_DIR,
                self.logic,
                self.track.split('/')[-1]]
        path = ''
        for d in dirs:
            path = os.path.join(path, d)
            if not os.path.exists(path):
                os.mkdir(path)
        return path

    ## Makes plots in results
    def mk_plots(self):
        plt.cla()
        plt.clf()
        plot_data = []
        full_db = get_db()

        #individual solvers
        for solver in self.solvers:
            rt = []
            for inst in self.db[solver]:
                rt.append(full_db.compute_score(logic=self.logic,track=self.track,solver=solver,inst=inst))
            plot_data.append((solver,rt))

        #vb solver
        vb = []
        for inst in self.db[self.solvers[0]]:
            vb_rt = float('+inf')
            for solver in self.solvers:
                vb_rt = min(vb_rt, full_db.compute_score(logic=self.logic,track=self.track,solver=solver,inst=inst))
            vb.append(vb_rt)
        plot_data.append(('Virtual Best', vb))

        #Random Solver
        plot_data.append(('Random Selection', [full_db.compute_score(logic=self.logic,track=self.track,solver=self.random_selections[it],inst=self.inputs[it]) for it in range(len(self.X))]))


        #machsmt
        plot_data.append(('MachSMT', [full_db.compute_score(logic=self.logic,track=self.track,solver=self.selections[it],inst=self.inputs[it]) for it in range(len(self.X))]))
        
        import itertools
        marker = itertools.cycle((',', '+', '.', 'o', '*')) 
        colors = itertools.cycle(('b','g','r','c','m','y')) 

        for d in plot_data:
            d[1].sort()
            if d[0] != 'MachSMT':
                plt.plot([v for v in d[1] if v < settings.TIMEOUT], label=d[0],marker=next(marker),color=next(colors))
            else:
                plt.plot([v for v in d[1] if v < settings.TIMEOUT], label=d[0],color='purple',marker='d')
            self.scoring[d[0]] = sum(d[1])

        plt.legend()
        plt.savefig(os.path.join(self.get_results_path(), 'plot.png'),dpi=700)
        plt.cla()
        plt.clf()

        pickle.dump(plot_data, open(os.path.join(self.get_results_path(), 'plot_data.p'), "wb" ))


    ##Makes CSVs in results 
    def log(self):
        track = self.track
        with open(os.path.join(self.get_results_path(), 'selections.csv'),'w') as file:
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
        
        with open(os.path.join(self.get_results_path(), 'par2.csv'),'w') as file:
            data = []
            for solver in self.scoring:
                data.append((solver,self.scoring[solver]))
            data.sort(key=lambda x:x[1])
            file.write('solver,score\n')
            for solver,par2 in data:
                file.write(solver + ',' + str(par2) + '\n')
    

    ## Final testing procedure
    def predict(self, file):
        X = np.array(get_features(file_path=file,logic=self.logic,track=self.track))
        Y = []
        for solver in self.solvers:
            Y.append(self.lm[solver].predict(X.reshape(1, -1))[0])
        return self.solvers[np.argmin(Y)]

    ##Main function
    def run(self):
        self.calc_features()
        if len(self.X) < 5: ##Awkward place to check... fix soon
            print("Track too small to consider (only " + str(len(self.X)) + " inputs)")
            return
        self.eval()
        self.build()
        self.baseline()
        self.mk_plots()
        self.log()
