import os,pickle,pdb,itertools
import machsmt.predictors as predictor
import matplotlib.pyplot as plt
from .db import database as db
from .smtlib import get_contest_data
from .parser import args as settings
from .util import warning

class MachSMT:
    def __init__(self):
        ######
        # Settings
        ######
        self.predictors = (         ## The following are ran
            predictor.Random,       
            predictor.Oracle,
            predictor.Greedy,
            predictor.Solver,
            predictor.SolverTrack,
            predictor.SolverLogic,
            predictor.SolverTrackLogic,
            predictor.PairWise,
        )
        self.smtcomp_years = 2019,  ## The following years are evaluated.

        ##Storage
        self.predictions = {}
        self.smtcomp_data  = {}

    def eval(self,predictors=[],logics=[],tracks=[]):
        benchmarks = []
        predictors = (v() for v in self.predictors) if not predictors else predictors
        for logic in (logics if logics else db.get_logics()):
            for track in  (tracks if tracks else db.get_tracks()):
                benchmarks += db.get_benchmarks(logic=logic,track=track)
        for pred in predictors: 
            if pred.__class__.__name__ not in self.predictions:
                self.predictions[pred.__class__.__name__] = pred.eval(benchmarks)
    def save(self):
        for algo in self.predictions:
            try:
                os.makedirs(os.path.join(settings.lib, 'predictions'))
            except FileExistsError: pass

            with open(os.path.join(settings.lib, 'predictions', algo + '.dat'),'wb') as outfile:
                pickle.dump(self.predictions[algo], outfile)
        for year in self.smtcomp_data:
            try:
                os.makedirs(os.path.join(settings.lib, 'smtcomp'))
            except FileExistsError: pass

            with open(os.path.join(settings.lib, 'smtcomp', str(year) + '.dat'),'wb') as outfile:
                pickle.dump(self.smtcomp_data[year], outfile)
    
    def load(self):
        for algo in self.predictors:
            algo = algo.__name__
            try:
                with open(os.path.join(settings.lib, 'predictions', algo + '.dat'), 'rb') as infile:
                    self.predictions[algo] = pickle.load(infile)
            except FileNotFoundError:
                warning("Could not find predictor.", algo)
        for year in self.smtcomp_years:
            if year == None: continue
            try:
                with open(os.path.join(settings.lib, 'smtcomp', str(year) + '.dat') ,'rb') as infile:
                    self.smtcomp_data[year] = pickle.load(infile)
            except FileNotFoundError:
                warning("Could not find smtcomp data, trying to build it.")
                self.smtcomp_data[year] = get_contest_data(year)

    def compile_reuslts(self):
        ##First SMT-COMP
        for year in self.smtcomp_years:
            for track in self.smtcomp_data[year]:
                for logic in self.smtcomp_data[year][track]:
                    ## Compute common benchmarks across SMT-COMP + MachSMT
                    comp_benchmarks,comp_solvers = set(),set()
                    for solver in self.smtcomp_data[year][track][logic]:
                        comp_solvers.add(solver)
                        for benchmark in self.smtcomp_data[year][track][logic][solver]: comp_benchmarks.add(benchmark)
                    common_benchmarks = set(comp_benchmarks)
                    for solver in self.smtcomp_data[year][track][logic]:
                        solver_benchmarks = set(b for b in self.smtcomp_data[year][track][logic][solver])
                        common_benchmarks = set(b for b in common_benchmarks if b in solver_benchmarks)
                        if len(comp_benchmarks) - len(solver_benchmarks) != 0:
                            warning("SMTCOMP -- Solver [" + solver + '] missing: ' + str(len(comp_benchmarks) - len(solver_benchmarks)) + "/" + str(len(comp_benchmarks)) + " benchmarks.",logic,track,year)
                    if len(comp_benchmarks) - len(common_benchmarks) > 0: 
                        warning("SMTCOMP -- Lost " + str(len(comp_benchmarks) - len(common_benchmarks)) +  "/" + str(len(comp_benchmarks)) + " benchmarks, due to inconsistentcy.",year,track,logic)
                    benchmarks = set(db.get_benchmarks()).intersection(set(b for b in common_benchmarks))
                    if len(common_benchmarks) - len(benchmarks) > 0: 
                        warning("SMTCOMP -- Lost " + str(len(common_benchmarks) - len(benchmarks)) +  "/" + str(len(common_benchmarks)) + " benchmarks. They are missing from MachSMT's database.",year,track,logic)

                    ## Generate Plot Data
                    # first SMT-COMP
                    plot_data = {}
                    for solver in comp_solvers:
                        if solver.lower().find('par4') != -1: continue
                        plot_data[solver] = []
                        for benchmark in benchmarks:
                            plot_data[solver].append(db[solver,benchmark])
                    # last, gather predictors
                    for algo in self.predictions:
                        plot_data[algo] = []
                        for benchmark in benchmarks:
                            try:
                                best = min(self.predictions[algo][benchmark],key=lambda p:self.predictions[algo][benchmark][p])
                                plot_data[algo].append(db[best,benchmark])
                            except:
                                warning('Missing prediction:' , algo, benchmark)
                                try :
                                    winner = min(self.predictions['Greedy'][benchmark],key=lambda p:self.predictions['Greedy'][benchmark][p])
                                except TypeError:
                                    winner = self.predictions['Greedy'][benchmark]
                                    plot_data[algo].append(db[best,benchmark])
                    loc = settings.results+ '/smt-comp/'+ str(year)+ '/' + track+'/'+logic + '/'
                    self.mk_plot(plot_data, title="SMT-COMP '" + str(year%1000) + ' -- ' + logic + ' ' + track, loc=loc)
                    self.mk_score_file(plot_data,loc=loc)
                    self.mk_loss_file(benchmarks=benchmarks, loc=loc)

        ##Now, what is in DB
        for track in sorted(db.get_tracks()):
            for logic in sorted(db.get_logics(track=track)):
                division_benchmarks = set(db.get_benchmarks(track=track,logic=logic))
                common_benchmarks   = set(db.get_benchmarks(track=track,logic=logic))
                for solver in sorted(db.get_solvers(logic=logic,track=track)):
                    solver_benchmarks = set(db.get_benchmarks(solver=solver,logic=logic,track=track))
                    common_benchmarks = common_benchmarks.intersection(solver_benchmarks)
                    if len(solver_benchmarks) - len(division_benchmarks) != 0:
                        warning("Solver [" + solver + '] missing: ' + str(len(division_benchmarks) - len(solver_benchmarks)) + "/" + str(len(division_benchmarks)) + " benchmarks.",logic,track,year)
                if len(common_benchmarks) - len(division_benchmarks) != 0: 
                    warning("SMTCOMP -- Lost " + str(len(common_benchmarks) - len(division_benchmarks)) +  "/" + str(len(division_benchmarks)) + " benchmarks. They are missing from MachSMT's database.",year,track,logic)
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
                            best = min(self.predictions[algo][benchmark],key=lambda p:self.predictions[algo][benchmark][p])
                            plot_data[algo].append(db[best,benchmark])
                        except:
                            warning('Missing prediction:' , algo, benchmark)
                            best = min(self.predictions['Greedy'][benchmark],key=lambda p:self.predictions['Greedy'][benchmark][p])
                            plot_data[algo].append(db[best,benchmark])
                loc = settings.results+ '/' + track+'/'+logic + '/'
                self.mk_plot(plot_data, title='MachSMT Evaluation -- ' + logic + ' ' + track, loc=loc)
                self.mk_score_file(plot_data,loc=loc)
                self.mk_loss_file(benchmarks=common_benchmarks, loc=loc)

    def mk_plot(self,plot_data,title,loc):
        return
        plt.cla()
        plt.clf()
        marker = itertools.cycle((',', '+', 'o', '*'))
        colors = itertools.cycle(('b','g','r','c','m','y'))
        for solver in plot_data:
            plt.plot(sorted((v for v in sorted(plot_data[solver]) if v != None)), label=solver,marker=next(marker),color=next(colors))
        plt.legend()
        os.makedirs(loc,exist_ok=True)
        plt.savefig(loc+'cactus.png',dpi=1000)

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
                lossfile.write('benchmark,prediction,loss')
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
                    lossfile.write(benchmark + ',' + prediction + ',' + str(loss) + '\n')




    def mk_scatter(self,plot_data,loc):
        for algo in self.predictions:
            if algo not in plot_data: continue
