import matplotlib.pyplot as plt
import os, pdb, csv
import itertools
import numpy as np
from ..config import config
from .. import MachSMT
from ..solver import Solver
from sklearn.model_selection import KFold

class Evaluator:
    def __init__(self, db) -> None:
        self.db = db
        self.mach = MachSMT(self.db)
        self.mach_predictions = []

    def mk_plot_data(self, benchmarks):
        ret = dict(
            (solver.get_name(), [])
            for solver in self.db.get_solvers()
        )
        ret['Virtual Best'] = []
        ret['MachSMT'] = []
        for it, benchmark in enumerate(benchmarks):
            scores = []
            for solver in self.db.get_solvers():
                scores.append(self.db.get_score(
                    solver=solver, benchmark=benchmark
                ))
                ret[solver.get_name()].append(scores[-1])
            ret['MachSMT'].append(self.mach_predictions[it])
            ret['Virtual Best'].append(min(scores))
        return ret
        
    def mk_plot(self,plot_data,title,loc):
        max_score = config.max_score

        # Escape _ for latex
        title = title.replace('_', '\\_')

        plt.rc('text', usetex=False) ##setting false for artifact only!
        os.makedirs(loc, exist_ok=True)

        # Sort solvers by number of solved instances
        ranked_solvers = sorted(plot_data, key=lambda s: sum(t < max_score for t in plot_data[s]), reverse=True)
        for plot_type in ('cdf', 'cactus'):
            plt.cla()
            plt.clf()

            markers = itertools.cycle((',', '+', 'o', '*'))
            colors = itertools.cycle(('b','g','r','c','m','y'))

            # sort by number of solved instances
            for solver in ranked_solvers:
                X = sorted(v for v in plot_data[solver] if v < max_score)
                Y = list(range(1,len(X)+1))
                solver_name = solver
                color, marker = next(colors), next(markers)

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
            plt.savefig(f"{loc}/{plot_type}.png", dpi=1000, bbox_inches='tight')

    def mk_par2_file(self,plot_data,path):
        data = dict(
            (solver, sum(plot_data[solver]))
            for solver in plot_data
        )
        cols = ['Solver', 'Par-2 Score', 'Improvement']
        mach_score = data['MachSMT']
        with open(path, 'w') as outcsv:
            out = csv.DictWriter(outcsv, fieldnames=cols)
            out.writeheader()
            for solver in sorted(data, key=data.get):
                score = data[solver]
                mach_improve = (score - mach_score) / ((score + mach_score) / 2.0) 
                if isinstance(solver, Solver): solver = solver.get_name()
                out.writerow({cols[0]: solver, cols[1]: score, cols[2]: mach_improve})

    def dump(self):
        for logic in self.db.get_logics():
            benchmarks = self.db.get_benchmarks(logic=logic)
            data = self.mk_plot_data(benchmarks=benchmarks)
            self.mk_plot(data, title=f'{logic=}',loc=f"{config.results}/{logic}")
            self.mk_par2_file(data,path=f"{config.results}/{logic}/scores.csv")
        benchmarks = self.db.get_benchmarks()
        data = self.mk_plot_data(benchmarks=benchmarks)
        self.mk_plot(data, title=f'All Benchmarks',loc=f"{config.results}/ALL")
        self.mk_par2_file(data,path=f"{config.results}/ALL/scores.csv")

    def run(self):
        self.mach.train()
        predictions = self.mach.predict()
        self.mach_predictions = [
            self.db.get_score(solver,benchmark) 
            for solver,benchmark in zip(predictions, self.db.get_benchmarks())
        ]
        self.dump()

    # def k_fold(self, benchmarks):
    #     benchmarks = np.array(benchmarks)
    #     ret = [None for _ in benchmarks]
    #     k_fold_args = {'n_splits': config.k, 'shuffle': True, 'random_state': config.rng}
    #     for train, test in KFold(**k_fold_args).split(benchmarks):
    #         self.mach.train(benchmarks=benchmarks[train])
    #         pred = self.mach.predict(benchmarks=benchmarks[test])
    #         for it, indx in enumerate(test):
    #             ret[indx] = pred[it]
    #     return ret
