import os,pickle,pdb,itertools
import machsmt.predictors as predictor
import matplotlib.pyplot as plt
from .db import database as db
from .smtlib import get_contest_data
from .parser import args as settings
from .util import warning

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
                            plot_data[algo].append(db[best,benchmark])
                        except:
                            warning('Missing prediction:' , algo, benchmark)
                            best = min(self.predictions['Greedy'][benchmark],key=self.predictions['Greedy'][benchmark].get) ##go with greedy on missing data.
                            plot_data[algo].append(db[best,benchmark])
                loc = settings.results+ '/' + track+'/'+logic + '/'
                if logic == "QF_BVFP": pdb.set_trace()
                self.mk_plots(plot_data, title='MachSMT Evaluation -- ' + logic + ' ' + track, loc=loc)
                self.mk_score_file(plot_data,loc=loc)
                self.mk_loss_file(benchmarks=common_benchmarks, loc=loc)



    def mk_plots(self,plot_data,title,loc):
        plt.cla()
        plt.clf()
        marker = itertools.cycle((',', '+', 'o', '*'))
        colors = itertools.cycle(('b','g','r','c','m','y'))
        for solver in plot_data:
            Y = sorted((v for v in sorted(plot_data[solver]) if v != None))
            X = list(range(1,len(Y)+1))
            plt.plot(X,Y,label=solver,marker=next(marker),color=next(colors))
        plt.legend()
        os.makedirs(loc,exist_ok=True)
        plt.xlabel("Number of benchmarks Solved")
        plt.ylabel("Score")
        plt.title(title)
        plt.savefig(loc+'cactus.png',dpi=1000)

        plt.cla()
        plt.clf()
        marker = itertools.cycle((',', '+', 'o', '*'))
        colors = itertools.cycle(('b','g','r','c','m','y'))
        for solver in plot_data:
            Y = sorted((v for v in sorted(plot_data[solver]) if v != None))
            X = list(range(1,len(Y)+1))
            plt.plot(Y,X,label=solver,marker=next(marker),color=next(colors))
        plt.legend()
        os.makedirs(loc,exist_ok=True)
        plt.ylabel("Number of benchmarks Solved")
        plt.xlabel("Score")
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