import pdb,os,sys,random,pickle,os,glob,itertools,traceback
import numpy as np
import machsmt.settings as settings
from machsmt.util import die,warning
from machsmt.benchmark import Benchmark
from sklearn.model_selection import LeaveOneOut,KFold
from progress.bar import Bar
from machsmt.smtlib import logic_list,get_theories
import matplotlib.pyplot as plt
import multiprocessing.dummy as mp

from machsmt.predictor import *

class ModelEvaluator:
    ##Init
    def __init__(self,db):
        self.db = db
        self.structure = None
        self.smtcomp = None
        self.smtcomp_plot_data = None
        self.plot_data = None

        self.predictors = {
            "MachSMT-S":    SolverPredictor(self.db),
            "MachSMT-LT":   LogicTrackPredictor(self.db),
            # "MachSMT-LTC":  LogicTrackPredictor(self.db,common=True),
            "MachSMT-PWS":  PairwisePredictor(self.db),
        }

    ## Parse SMT data, and load plot data
    def parse_smtcomp(self):
        ## Build data structure of all data
        if self.smtcomp == None:
            print("Loading SMT COMP data for comparisons.")
            self.smtcomp = {}
            for file in glob.glob('smt-comp/2019/results/*.csv'):
                with open(file) as infile:
                    self.smtcomp[file]               = {}
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
                            if logic not in self.smtcomp[file]:
                                self.smtcomp[file][logic] = {}
                                self.smtcomp[file][logic]['benchmarks']   = set()
                                self.smtcomp[file][logic]['solvers']      = set()
                            if line[bench] not in hasher: hasher[line[bench]] = Benchmark(line[bench]).path
                            if line[solver].lower().find('par4') != -1: continue
                            self.smtcomp[file][logic]['benchmarks'].add(hasher[line[bench]])
                            self.smtcomp[file][logic]['solvers'].add(line[solver])
            self.save()

        ## Populate Plot Data
        self.smtcomp_plot_data = {}
        for file in self.smtcomp:
            self.smtcomp_plot_data[file] = {}
            for logic in self.smtcomp[file]:
                self.smtcomp_plot_data[file][logic] = {}
                solvers = list(self.smtcomp[file][logic]['solvers'])
                benchmarks = set(self.smtcomp[file][logic]['benchmarks'])

                common_benchmarks = set(benchmarks)
                N = len(common_benchmarks)
                for solver in solvers:
                    solver_benchmarks = set(b for b in self.db.get_benchmarks(solver) if b in benchmarks)
                    common_benchmarks = set(b for b in common_benchmarks if b in solver_benchmarks)
                    if len(benchmarks) - len(solver_benchmarks) != 0: warning("Solver [" + solver + '] missing: ' + str(len(benchmarks) - len(solver_benchmarks)) + "/" + str(len(benchmarks)) + " benchmarks.",logic,file)
                if N - len(common_benchmarks) > 0: warning("Lost " + str(N - len(common_benchmarks)) +  "/" + str(len(benchmarks)) + " benchmarks.",logic,file)

                ## Generate virtual best data lines
                self.smtcomp_plot_data[file][logic]['Virtual Best'] = {}
                for solver in solvers:
                    self.smtcomp_plot_data[file][logic][solver] = {}
                    for benchmark in common_benchmarks:
                        self.smtcomp_plot_data[file][logic][solver][benchmark] = self.db[solver,benchmark]
                        self.smtcomp_plot_data[file][logic]['Virtual Best'][benchmark] = self.db[solver,benchmark] if benchmark not in self.smtcomp_plot_data[file][logic]['Virtual Best'] else min(self.smtcomp_plot_data[file][logic]['Virtual Best'][benchmark],self.db[solver,benchmark])

    ##set up structure and reuslts dir
    def organize(self):
        if not os.path.exists(settings.RESULTS_DIR): os.mkdir(settings.RESULTS_DIR)
        if not os.path.exists(settings.RESULTS_DIR + '/solvers'): os.mkdir(settings.RESULTS_DIR + '/solvers')
        if not os.path.exists(settings.RESULTS_DIR + '/tracks'):  os.mkdir(settings.RESULTS_DIR + '/tracks')
        self.structure = {}
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

    ## Construct results directory
    def smtcomp_plotter(self,logics=None):
        for file in self.smtcomp_plot_data:
            for logic in (self.smtcomp_plot_data[file] if logics == None else logics):
                solver = list(self.smtcomp_plot_data[file][logic].keys())[0]
                for benchmark in self.smtcomp_plot_data[file][logic][solver]:
                    for predictor in self.predictors:
                        if predictor not in self.smtcomp_plot_data[file][logic]:  self.smtcomp_plot_data[file][logic][predictor] = {}
                        try:
                            self.smtcomp_plot_data[file][logic][predictor][benchmark] = self.predictors[predictor].predictions[benchmark]
                        except:
                            die("Missing: ", file, logic, predictor,benchmark)


        marker = itertools.cycle((',', '+', '.', 'o', '*'))
        colors = itertools.cycle(('b','g','r','c','m','y')) 

        ### MAKE SMT COMP DATA
        if not os.path.exists(settings.RESULTS_DIR + '/smt-comp'):  os.mkdir(settings.RESULTS_DIR + '/smt-comp')
        for file in self.smtcomp_plot_data:
            if not os.path.exists(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','')):  os.mkdir(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv',''))
            for logic in self.smtcomp_plot_data[file]:
                score_data = []
                if not os.path.exists(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','') + '/' + logic):  os.mkdir(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','') + '/' + logic)
                plt.cla()
                plt.clf()
                for solver in self.smtcomp_plot_data[file][logic]:
                    scores = list(self.smtcomp_plot_data[file][logic][solver].values())
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
                with open(settings.RESULTS_DIR + '/smt-comp/' + file.split('/')[-1].replace('.csv','') + '/' + logic + '/loss.csv','w') as loss_file:
                    best_machsmt,score = None,float('+inf')
                    for solver in self.smtcomp_plot_data[file][logic]:
                        if solver.find('MachSMT') == -1: continue
                        s = sum(self.smtcomp_plot_data[file][logic][solver].values())
                        if s < score:
                            score,best_machsmt = s,solver
                    if best_machsmt == None:
                        warning("Can't find MachSMT for: " + logic, file)
                        continue


                    loss_data = []
                    loss_file.write('benchmark,loss\n')
                    for benchmark in self.smtcomp_plot_data[file][logic][best_machsmt]: loss_data.append((benchmark, self.smtcomp_plot_data[file][logic][best_machsmt][benchmark] - self.smtcomp_plot_data[file][logic]['Virtual Best'][benchmark]))
                    loss_data.sort(key=lambda v:v[1],reverse=True)
                    for benchmark,val in loss_data: loss_file.write(benchmark + ',' + str(val) + '\n')

    ## Save everything
    def save(self):
        with open(settings.RESULTS_DIR + '/data.p', 'wb') as outfile:
            pickle.dump(
                (
                    self.structure,
                    self.smtcomp,
                    self.smtcomp_plot_data,
                    self.plot_data,
                    self.predictors,
                ), 
            
            outfile)

    ## Load save
    def load(self):
        tmp_predictors = self.predictors
        if not os.path.exists(settings.RESULTS_DIR + '/data.p'): raise FileNotFoundError
        with open(settings.RESULTS_DIR + '/data.p', 'rb') as infile:
                    self.structure,\
                    self.smtcomp,\
                    self.smtcomp_plot_data,\
                    self.plot_data,\
                    = pickle.load(infile)
        self.predictors
        for val in tmp_predictors:
            self.predictors[val] = tmp_predictors[val]

    ## Main Method
    def run(self, logics = None):
        try:
            self.load()
        except:
            print("Building from scratch.")
        self.parse_smtcomp()
        self.organize()
        run = {
            "MachSMT-S":    False,
            "MachSMT-T":    False,
            "MachSMT-L":    False,
            "MachSMT-LT":   False,
            "MachSMT-LTC":  False,
            "MachSMT-PWS":  True
        }
        for algo in run:
            try:
                if run[algo]: self.predictors[algo].eval(logics)
            except Exception as ex:
                traceback.print_exception(type(ex), ex, ex.__traceback__)
            finally:
                self.save()
        if True: self.smtcomp_plotter(logics)
        self.save()