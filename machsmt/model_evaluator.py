import pdb,os,sys,random,pickle,os,glob
import numpy as np
from machsmt.model_maker import mk_regressor
import machsmt.settings as settings
from machsmt.util import die,warning
from machsmt.benchmark import Benchmark
from sklearn.model_selection import LeaveOneOut,KFold
from progress.bar import Bar
from machsmt.smtlib import logic_list
import matplotlib.pyplot as plt

class ModelEvaluator:
    def __init__(self,db):
        self.db = db
        self.structure = {}
        self.solver_predictions = {}
        self.logic_track_predictions  = {}

        self.smt_comp = {}

    def parse_smt_comp(self):
        for file in glob.glob('smt-comp/2019/results/*.csv'):
            with open(file) as infile:
                self.smt_comp[file]               = {}
                header = None
                bench,solver = None,None
                hasher = {}
                for it,line in enumerate(infile):
                    if it == 0: 
                        header = line.split(',')
                        bench,solver = header.index('benchmark'),header.index('solver')
                    else:
                        line = line.split(',')
                        logic = None
                        for v in line[bench].split('/'):
                            if v in logic_list: 
                                logic = v
                                break
                        assert logic != None
                        if logic not in self.smt_comp[file]:
                             self.smt_comp[file][logic] = {}
                             self.smt_comp[file][logic]['benchmarks']   = set()
                             self.smt_comp[file][logic]['solvers']      = set()
                        if line[bench] not in hasher: hasher[line[bench]] = Benchmark(line[bench]).path
                        if line[solver].lower().find('par4') == -1:
                            self.smt_comp[file][logic]['benchmarks'].add(hasher[line[bench]])
                            self.smt_comp[file][logic]['solvers'].add(line[solver])

    def organize(self):
        if not os.path.exists(settings.RESULTS_DIR): os.mkdir(settings.RESULTS_DIR)
        if not os.path.exists(settings.RESULTS_DIR + '/solvers'): os.mkdir(settings.RESULTS_DIR + '/solvers')
        if not os.path.exists(settings.RESULTS_DIR + '/tracks'):  os.mkdir(settings.RESULTS_DIR + '/tracks')

        for solver in self.db.get_solvers():
            for benchmark in self.db.get_benchmarks(solver):
                if self.db[benchmark].logic not in self.structure: self.structure[self.db[benchmark].logic] = {}
                if self.db[benchmark].track not in self.structure[self.db[benchmark].logic]: self.structure[self.db[benchmark].logic][self.db[benchmark].track] = []
                logic, track = self.db[benchmark].logic, self.db[benchmark].track
                if solver not in self.structure[logic][track]: self.structure[logic][track].append(solver)

        for logic in self.structure:
            if not os.path.exists(settings.RESULTS_DIR + '/tracks/' + logic): os.mkdir(settings.RESULTS_DIR + '/tracks/' + logic)
            for track in self.structure[logic]:
                if not os.path.exists(settings.RESULTS_DIR + '/tracks/' + logic + '/' + track): 
                    os.mkdir(settings.RESULTS_DIR + '/tracks/' + logic + '/' + track)

    def eval_solver_ehms(self):
        N = 0
        for solver in self.db.get_solvers(): 
            self.solver_predictions[solver] = {}
            N += 1

        bar = Bar('Building Solver EHMs', max=N)
        for solver in self.db.get_solvers():
            X, Y = [],[]
            benchmarks = list(self.db.get_benchmarks(solver))
            for benchmark in benchmarks:
                X.append(self.db[benchmark].get_features())
                Y.append(self.db[solver,benchmark])
            if len(X) < settings.K_FOLD:
                warning("Not enough data to evaluate EHM.",solver)
                continue
            ##
            X,Y = np.array(X), np.log(np.array(Y)+1)
            for train, test in KFold(n_splits=settings.K_FOLD,shuffle=True).split(X):
                predictions = mk_regressor(n_samples = len(X[train]), n_features = len(X[0])).fit(X[train],Y[train]).predict(X[test])
                for it, indx in enumerate(test):
                    self.solver_predictions[solver][benchmarks[indx]] = predictions[it]
            bar.next()
        bar.finish()

    def eval_logic_track_ehms(self):
        N = 0
        for logic in self.structure:
            self.logic_track_predictions[logic] = {}
            for track in self.structure[logic]:
                self.logic_track_predictions[logic][track]= {}
                for solver in self.structure[logic][track]:
                    self.logic_track_predictions[logic][track][solver] = {}
                    N += 1

        bar = Bar('Building Track EHMs', max=N)
        for logic in self.structure:
            for track in self.structure[logic]:
                for solver in self.structure[logic][track]:
                    X, Y = [],[]
                    all_benchmarks = list(self.db.get_benchmarks(solver))
                    benchmarks = []
                    for benchmark in all_benchmarks:
                        if self.db[benchmark].logic == logic and self.db[benchmark].track == track:
                            X.append(self.db[benchmark].get_features())
                            Y.append(self.db[solver,benchmark])
                            benchmarks.append(benchmark)
                    if len(X) < settings.K_FOLD:
                        warning("Not enough data to evaluate EHM.",solver,logic,track)
                        continue
                    ##
                    X,Y = np.array(X), np.log(np.array(Y)+1)
                    for train, test in KFold(n_splits=settings.K_FOLD,shuffle=True).split(X):
                        predictions = mk_regressor(n_samples = len(X[train]), n_features = len(X[0])).fit(X[train],Y[train]).predict(X[test])
                        for it, indx in enumerate(test):
                            self.logic_track_predictions[logic][track][solver][benchmarks[indx]] = predictions[it]
                    bar.next()
        bar.finish()

    def plotter(self):
        plot_data = {}
        for file in self.smt_comp:
            plot_data[file] = {}
            for logic in self.smt_comp[file]:
                plot_data[file][logic] = {}
                solvers = list(self.smt_comp[file][logic]['solvers'])
                benchmarks = self.smt_comp[file][logic]['benchmarks']

                common_benchmarks = set(benchmarks)
                N = len(common_benchmarks)
                for solver in solvers:
                    solver_benchmarks = set(self.db.get_benchmarks(solver))
                    common_benchmarks = set(b for b in common_benchmarks if b in solver_benchmarks)
                if len(common_benchmarks) < settings.K_FOLD:
                    warning("Not enough data to evaluate EHM.",file,logic)
                    continue

                warning("Lost " + str(N - len(common_benchmarks)) + " benchmarks.",logic,file)
                
                ## Generate virtual best + solver data lines
                plot_data[file][logic]['Virtual Best'] = {}
                for solver in solvers:
                    plot_data[file][logic][solver] = {}
                    for benchmark in common_benchmarks:
                        plot_data[file][logic][solver][benchmark] = self.db[solver,benchmark]
                        plot_data[file][logic]['Virtual Best'][benchmark] = self.db[solver,benchmark] if benchmark not in plot_data[file][logic]['Virtual Best'] else min(plot_data[file][logic]['Virtual Best'][benchmark],self.db[solver,benchmark])
                
                ## MachSMT lines
                plot_data[file][logic]['MachSMT'] = {}
                # plot_data[file][logic]['MachSMT - solver'] = {}
                for benchmark in common_benchmarks:
                    predicted_times = []
                    for solver in solvers:
                        try:
                            predicted_times.append(self.logic_track_predictions[logic][self.db[benchmark].track][solver][benchmark])         
                        except:
                            warning("Missing prediction: ", logic,benchmark,solver)
                            predicted_times.append(float('inf'))

                        # try:
                        #     predicted_times.append(self.solver_predictions[solver][benchmark])
                        # except:
                        #     warning("Missing prediction: ", logic,benchmark,solver)
                        #     predicted_times.append(float('inf'))
                    plot_data[file][logic]['MachSMT'][benchmark] = self.db[benchmark,solvers[np.argmin(predicted_times)]]

        import itertools
        marker = itertools.cycle((',', '+', '.', 'o', '*'))
        colors = itertools.cycle(('b','g','r','c','m','y')) 

        ### MAKE SMT COMP DATA
        if not os.path.exists(settings.RESULTS_DIR + '/smt-comp'):  os.mkdir(settings.RESULTS_DIR + '/smt-comp')
        for file in plot_data:
            if not os.path.exists(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','')):  os.mkdir(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv',''))
            for logic in plot_data[file]:
                score_data = []
                if not os.path.exists(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','') + '/' + logic):  os.mkdir(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','') + '/' + logic)
                plt.cla()
                plt.clf()
                for solver in plot_data[file][logic]:
                    scores = list(plot_data[file][logic][solver].values())
                    scores.sort()
                    plt.plot(scores,label=solver,marker=next(marker),color=next(colors))
                    score_data.append((solver,sum(scores)))
                plt.legend()
                plt.savefig(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','') + '/' + logic + '/cactus.png',dpi=700)
                with open(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','') + '/' + logic + '/scores.csv','w') as score_file:
                    score_data.sort(key=lambda p:p[1])
                    score_file.write("solver,score\n")
                    for solver,score in score_data:
                        score_file.write(solver + "," + str(score) + "\n")

    def save(self):
        with open(settings.RESULTS_DIR + '/data.p', 'wb') as outfile:
            pickle.dump((self.structure, self.solver_predictions, self.logic_track_predictions, self.smt_comp), outfile)

    def load(self):
        if not os.path.exists(settings.RESULTS_DIR + '/data.p'): raise FileNotFoundError
        with open(settings.RESULTS_DIR + '/data.p', 'rb') as infile:
            self.structure, self.solver_predictions, self.logic_track_predictions, self.smt_comp = pickle.load(infile)

    def run(self,rerun=False):
        if rerun or not os.path.exists(settings.RESULTS_DIR + '/data.p'):
            self.parse_smt_comp()
            self.organize()
            self.eval_logic_track_ehms()
            self.eval_solver_ehms()
            self.save()
        else: self.load()
        self.eval_logic_track_ehms()
        # self.eval_solver_ehms()
        self.plotter()