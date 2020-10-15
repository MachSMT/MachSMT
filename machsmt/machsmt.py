import os,pickle,pdb,itertools
import machsmt.predictors as predictor
import matplotlib.pyplot as plt
from .db import database as db
from .smtlib import get_contest_data
from .parser import args as settings
from .util import warning
import numpy as np

class MachSMT:
    ##Initializer
    def __init__(self):
        self.predictors = (         
            predictor.Random,       #0
            predictor.Oracle,       #1
            predictor.Greedy,       #2
            predictor.Solver,       #3
            predictor.SolverLogic,  #4
            predictor.PairWise,     #5
            predictor.PairWiseLogic #6
        )
        self.default_predictor = 4

        self.core_predictor = None

        ##Storage
        self.predictions = {}   ## Map of Predictor x Benchmark x Solver x Predicted Time
        self.smtcomp_data  = {} ## collection of SMT-COMP data for evaluation purposes
        self.smtcomp_year = None

    ##Evaluate predictors on logics/tracks
    ## default all predictors/logics
    ## initializer syntax is misleading TODO: Fix
    def eval(self,predictors=[],logics=[],tracks=[]):
        benchmarks = []
        predictors = (v() for v in self.predictors) if not predictors else predictors
        for pred in predictors: 
            if pred.__class__.__name__ not in self.predictions:
                self.predictions[pred.__class__.__name__] = pred.eval()

    def build(self):
        self.core_predictor = self.predictors[self.default_predictor]()
        self.core_predictor.build()
        with open(settings.lib + '/default.dat', 'wb') as outfile:
            pickle.dump(self.core_predictor, outfile)

    def predict(self,benchmark):
        if self.core_predictor == None:
            if not os.path.exists(settings.lib + '/default.dat'): raise FileNotFoundError
            with open(settings.lib + '/default.dat', 'rb') as infile:
                self.core_predictor = pickle.load(infile)
        self.core_predictor.predict(benchmark)

    ##Save everything
    def save(self):
        for algo in self.predictions:
            try:
                os.makedirs(os.path.join(settings.lib, 'predictions'))
            except FileExistsError: pass

            with open(os.path.join(settings.lib, 'predictions', f'{algo}.dat'),'wb') as outfile:
                pickle.dump(self.predictions[algo], outfile)
        if self.smtcomp_year:
            try:
                os.makedirs(os.path.join(settings.lib, 'smtcomp'))
            except FileExistsError: 
                pass
            with open(os.path.join(settings.lib, 'smtcomp', f"{self.smtcomp_year}.dat"),'wb') as outfile:
                pickle.dump(self.smtcomp_data, outfile)
    
    ##Load everything that is available
    def load(self,smtcomp_year=None):
        self.smtcomp_year = smtcomp_year
        for algo in self.predictors:
            algo = algo.__name__
            try:
                with open(os.path.join(settings.lib, 'predictions', algo + '.dat'), 'rb') as infile:
                    self.predictions[algo] = pickle.load(infile)
            except FileNotFoundError:
                warning("Could not find predictor.", algo)
        if smtcomp_year:
            try:
                with open(os.path.join(settings.lib, 'smtcomp', str(smtcomp_year) + '.dat') ,'rb') as infile:
                    self.smtcomp = pickle.load(infile)
            except FileNotFoundError:
                warning("Could not find smtcomp data, trying to build it.")
                self.smtcomp_data = get_contest_data(smtcomp_year)

    def compile_results(self):
        ##Now, what is in DB
        for track in sorted(db.get_tracks()):
            logics = set(sorted(db.get_logics(track=track)))
            if settings.logics:
                logics = logics.intersection(set(settings.logics))
            for logic in logics:
                division_benchmarks = set(db.get_benchmarks(track=track,logic=logic))
                common_benchmarks   = set(db.get_benchmarks(track=track,logic=logic))
                for solver in sorted(db.get_solvers(logic=logic,track=track)):
                    solver_benchmarks = set(db.get_benchmarks(solver=solver,logic=logic,track=track))
                    common_benchmarks = common_benchmarks.intersection(solver_benchmarks)
                    if len(solver_benchmarks) - len(division_benchmarks) != 0:
                        warning(f"Solver [{solver}] missing: {len(division_benchmarks) - len(solver_benchmarks)}/{len(division_benchmarks)} benchmarks.",logic,track)
                if len(common_benchmarks) - len(division_benchmarks) != 0: 
                    warning(f"Lost{len(common_benchmarks) - len(division_benchmarks)}/{len(division_benchmarks)} benchmarks. They are missing from MachSMT's database.",track,logic)
                plot_data = {}
                #first, gather solvers in db
                for solver in db.get_solvers(track=track,logic=logic):
                    plot_data[solver] = []
                    for benchmark in common_benchmarks:
                        plot_data[solver].append(db[solver,benchmark])
                # last, gather predictors
                for algo in self.predictions:
                    plot_data[algo] = []
                    for benchmark in common_benchmarks:
                        try:
                            best = min(self.predictions[algo][benchmark],key=self.predictions[algo][benchmark].get)
                            score = db[best,benchmark]
                        except:
                            warning('Missing prediction:' , algo, benchmark)
                            best = min(self.predictions['Greedy'][benchmark],key=self.predictions['Greedy'][benchmark].get) ##go with greedy on missing data.
                        score = db[best,benchmark]
                        if algo != 'Oracle' and settings.include_feature_times:
                            score += db[benchmark].total_feature_time
                        plot_data[algo].append(score)
                loc = settings.results+ '/' + track+'/'+logic + '/'
                # if logic == "QF_BVFP": pdb.set_trace()
                self.mk_plots(plot_data, title='MachSMT Evaluation -- ' + logic + ' ' + track, loc=loc)
                self.mk_score_file(plot_data,loc=loc)
                self.mk_loss_file(benchmarks=common_benchmarks, loc=loc)



    def mk_plots(self,plot_data,title,loc):
        #from stackoverflow

        lim_axis = True
        legend = False
        cactus_x = [560, 800]
        cactus_y = [-5, 1200]
        max_score = 1200

        def reorderLegend(ax=None,order=None,unique=False):
            ax=plt.gca()
            handles, labels = ax.get_legend_handles_labels()
            labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0])) # sort both labels and handles by labels
            if order is not None: # Sort according to a given list (not necessarily complete)
                keys=dict(zip(order,range(len(order))))
                labels, handles = zip(*sorted(zip(labels, handles), key=lambda t,keys=keys: keys.get(t[0],np.inf)))
            if unique:  labels, handles= zip(*unique_everseen(zip(labels,handles), key = labels)) # Keep only the first of each handle
            ax.legend(handles, labels)
            return(handles, labels)
        aliases = {
            'Random':'MachSMT-Random',
            'Oracle': 'Virtual Best Solver',
            'Greedy':'MachSMT-Greedy',
            'Solver':'MachSMT-SolverEHM',
            'SolverLogic': 'MachSMT-SolverLogicEHM',
            'PairWise': 'MachSMT-SolverPWC',
            'PairWiseLogic': 'MachSMT-SolverLogicPWC',
        }
        aliased_data = {}
        for k in plot_data:
            if k not in aliases:
                aliased_data[k] = plot_data[k]
            else:
                aliased_data[aliases[k]] = plot_data[k]

        color_markers = {
            'MachSMT-Random': ('olive', 'x'),
            'Virtual Best Solver': ('black', '+'),
            'MachSMT-Greedy': ('olive', '|'),
            'MachSMT-SolverEHM': ('green', 'p'),
            'MachSMT-SolverLogicEHM': ('purple', '*'),
            'MachSMT-SolverPWC': ('cyan', 's'),
            'MachSMT-SolverLogicPWC': ('red', '2'),
        }
        plt.cla()
        plt.clf()
        markers= itertools.cycle((',', '+', 'o', '*'))
        colors = itertools.cycle(('b','g','r','c','m','y'))
        for solver in aliased_data:
            Y = sorted((v for v in aliased_data[solver] if v < max_score))
            X = list(range(1,len(Y)+1))
            solver_name = solver if solver not in aliases else aliases[solver]
            color,marker = (next(colors),next(markers)) if solver not in color_markers else color_markers[solver]
            plt.plot(X,Y,label=solver_name,marker=marker,color=color,markevery=1,linewidth=1, markersize=6)
        os.makedirs(loc,exist_ok=True)
        plt.xlabel("Number of benchmarks Solved")
        plt.ylabel("Wallclock Runtime")
        plt.title(title)
        if legend: 
            plt.legend()
            reorderLegend(order=sorted(aliased_data.keys(),key=lambda s: sum(aliased_data[s])))

        if legend:
            handles,labels = plt.gca().get_legend_handles_labels()
            fig_legend = plt.figure(figsize=(10,10))
            axi = fig_legend.add_subplot(111)            
            fig_legend.legend(handles, labels, loc='center', scatterpoints = 1)
            axi.xaxis.set_visible(False)
            axi.yaxis.set_visible(False)
            # fig_legend.canvas.draw()
            fig_legend.savefig(loc+'asdf.png',dpi=1000)

        
        if lim_axis:
            plt.xlim(cactus_x) 
            plt.ylim(cactus_y) 
        plt.savefig(loc+'cactus.png',dpi=1000)
        

        plt.cla()
        plt.clf()
        marker = itertools.cycle((',', '+', 'o', '*'))
        colors = itertools.cycle(('b','g','r','c','m','y'))
        for solver in aliased_data:
            Y = sorted((v for v in aliased_data[solver] if v < max_score))
            X = list(range(1,len(Y)+1))
            solver_name = solver if solver not in aliases else aliases[solver]
            color,marker = (next(colors),next(markers),) if solver not in color_markers else color_markers[solver]
            plt.plot(Y,X,label=solver_name,marker=marker,color=color,markevery=1,linewidth=1, markersize=6)
        if legend: 
            plt.legend()
            reorderLegend(order=sorted(aliased_data.keys(),key=lambda s: sum(aliased_data[s])))
        os.makedirs(loc,exist_ok=True)
        
        if lim_axis:
            plt.ylim(cactus_x) 
            plt.xlim(cactus_y) 
        plt.ylabel("Number of benchmarks Solved")
        plt.xlabel("Wallclock Runtime")
        plt.title(title)
        plt.savefig(loc+'cdf.png',dpi=1000)


    def mk_score_file(self,plot_data,loc):
        with open(loc + 'scores.csv','w') as scorefile:
            score_data = []
            scorefile.write('solver,score\n')
            for solver in plot_data:
                score_data.append((solver,sum(plot_data[solver])))
            score_data.sort(key=lambda v:v[1])
            for solver,score in score_data:
                scorefile.write(solver + ',' + str(score) + '\n')
            
    def mk_loss_file(self,benchmarks,loc):
        for algo in self.predictions.keys():
            with open(loc + algo + '_loss.csv','w') as lossfile:
                lossfile.write('benchmark,prediction,loss\n')
                loss_data = []
                for benchmark in benchmarks:
                    try:
                        winner = min(self.predictions[algo][benchmark],key=lambda p:self.predictions[algo][benchmark][p])
                    except:
                        try :
                            winner = min(self.predictions['Greedy'][benchmark],key=lambda p:self.predictions['Greedy'][benchmark][p])
                        except TypeError:
                            winner = self.predictions['Greedy'][benchmark]
                    best   = min(self.predictions['Oracle'][benchmark],key=lambda p:self.predictions['Oracle'][benchmark][p])
                    loss_data.append(
                        (
                            benchmark,
                            winner,
                            db[winner,benchmark] - db[best,benchmark]
                        )
                    )
                for benchmark,prediction,loss in sorted(loss_data,key=lambda p: p[2], reverse=True):
                    lossfile.write(f"{benchmark},{prediction},{loss}\n")

    def mk_scatter(self,plot_data,loc):
        for algo in self.predictions:
            if algo not in plot_data: continue