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
            # predictor.PairWise,     #5
            # predictor.PairWiseLogic #6
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
                self.mk_plots(plot_data, title=f'{logic} ({track})', loc=loc)
                self.mk_score_file(plot_data,loc=loc)
                self.mk_loss_file(benchmarks=common_benchmarks, loc=loc)


    def mk_plots(self,plot_data,title,loc):

        max_score = 1200

        # Escape _ for latex
        title = title.replace('_', '\\_')

        aliases = {
            'Random':'Mach-Random',
            'Oracle': 'VBS',
            'Greedy':'Mach-Greedy',
            'Solver':'Mach-EHM',
            'SolverLogic': 'Mach-LogicEHM',
            'PairWise': 'Mach-PWC',
            'PairWiseLogic': 'Mach-LogicPWC',
        }

        color_markers = {
            'Mach-Random': ('olive', 'x'),
            'VBS': ('black', '+'),
            'Mach-Greedy': ('olive', '|'),
            'Mach-EHM': ('green', 'p'),
            'Mach-LogicEHM': ('purple', '*'),
            'Mach-PWC': ('cyan', 's'),
            'Mach-LogicPWC': ('red', '2'),
        }

        def cleanup_solver_name(name):
            name = name.replace('-wrapped-sq', '')

            if name.startswith('master-2018'):
                name = 'CVC4 (2018)'
            elif name.startswith('CVC4-2019') or name == 'CVC4-sq-final':
                name = 'CVC4'
            elif name == 'z3-4.7.1':
                name = 'Z3 (2018)'
            elif name.startswith('z3'):
                name = 'Z3'
            elif name.startswith('COLIBRI'):
                name = 'COLIBRI'
            elif name.startswith('smtinterpol'):
                name = 'SMTInterpol'
            elif name.startswith('Yices 2.6.2'):
                name = 'Yices 2.6.2'
            elif name.startswith('vampire-4.3'):
                name = 'Vampire (2018)'
            elif name.startswith('vampire-4.4'):
                name = 'Vampire (2019)'
            elif name.startswith('vampire'):
                name = 'Vampire'

            return name

        aliased_data = {}
        for k in plot_data:
            if k not in aliases:
                aliased_data[k] = plot_data[k]
            else:
                aliased_data[aliases[k]] = plot_data[k]


        plt.rc('text', usetex=False) ##setting false for artifact only!
        os.makedirs(loc, exist_ok=True)

        # Sort solvers by number of solved instances
        ranked_solvers = sorted(aliased_data, key=lambda s: sum(t < max_score for t in aliased_data[s]), reverse=True)
        for plot_type in ('cdf', 'cactus'):
            plt.cla()
            plt.clf()

            markers = itertools.cycle((',', '+', 'o', '*'))
            colors = itertools.cycle(('b','g','r','c','m','y'))

            # sort by number of solved instances
            for solver in ranked_solvers:
                X = sorted(v for v in aliased_data[solver] if v < max_score)
                Y = list(range(1,len(X)+1))
                solver_name = aliases.get(solver, cleanup_solver_name(solver))
                color,marker = color_markers.get(solver, (next(colors),next(markers),))

                if plot_type == 'cactus':
                    X, Y = Y, X

                plt.plot(X,Y,label=solver_name,marker=marker,color=color,markevery=1,linewidth=1, markersize=3)

            xlabel = 'Wallclock Runtime [s]'
            ylabel = 'Solved Benchmarks'
            lloc = 'lower right'
            if plot_type == 'cactus':
                lloc = 'upper left'
                xlabel, ylabel = ylabel, xlabel

            plt.legend(loc=lloc, prop={'size': 7})
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            plt.savefig(loc+'{}.png'.format(plot_type), dpi=1000, bbox_inches='tight')


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
