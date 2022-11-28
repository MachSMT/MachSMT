from ast import arg
from cmath import log
from .benchmark.benchmark import Benchmark
from .selectors import Greedy, GreedyLogic, EHM, EHMLogic, PWC, PWCLogic
from .solver import Solver
import csv
import pickle
import os
import itertools
from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np

from .util import warning, die
from .config import args
from .database import DataBase
from .exceptions import MachSMT_IncompleteDataError


class MachSMT:
    def __init__(self, data, train_on_init=True):
        if isinstance(data, DataBase):
            self.db = data
        elif isinstance(data, (str, os.PathLike)):
            self.db = DataBase(data)
        elif isinstance(data, Iterable):
            for v in data:
                if not isinstance(v, (str, os.PathLike)):
                    die(f"Unexpected value: {v}")
            self.db = DataBase(data)
        else:
            die(f"Unexpected value: {data}")
        if not self.db.is_complete():
            raise MachSMT_IncompleteDataError

        self.multi_logic = len(self.db.get_logics()) > 1
        
        self.selectors = {}
        self.selectors['EHM'] = EHM(self.db)
        self.default_selector = 'EHM'
        if self.multi_logic and args.logic_filter:
            self.selectors['EHMLogic'] = EHMLogic(self.db)
            self.default_selector = 'EHMLogic'
        if args.greedy:
            self.selectors['Greedy'] = Greedy(self.db)
            if self.multi_logic and args.logic_filter:
                self.selectors['GreedyLogic'] = GreedyLogic(self.db)
        if args.pwc:
            self.selectors['PWC'] = PWC(self.db)
            if self.multi_logic and args.logic_filter:
                self.selectors['PWCLogic'] = PWCLogic(self.db)
        
        if train_on_init: self.train()

    def train(self, benchmarks=None):
        if benchmarks is None:
            benchmarks = self.db.get_benchmarks()
        for algo_name, algo in self.selectors.items():
            algo.train(benchmarks)

    def eval(self, benchmarks=None):
        if benchmarks is None:
            benchmarks = self.db.get_benchmarks()
        predictions = {}
        for algo_name, algo in self.selectors.items():
            predictions[algo_name] = algo.eval(benchmarks)
        plot_data = {logic: {} for logic in self.db.get_logics()}
        vbs = 'Virtual Best'
        for it, benchmark in enumerate(benchmarks):
            logic = benchmark.get_logic()
            vbs_score = float('inf')
            for solver in self.db.get_solvers():
                if solver.get_name() not in plot_data[logic]: plot_data[logic][solver.get_name()] = []
                score = self.db.get_score(solver=solver, benchmark=benchmark)
                vbs_score = min(vbs_score, score)
                plot_data[logic][solver.get_name()].append(score)
            if vbs not in plot_data[logic]:
                plot_data[logic][vbs] = []
            plot_data[logic][vbs].append(vbs_score)
            for algo_name in predictions:
                if algo_name not in plot_data[logic]: plot_data[logic][algo_name] = []
                predicted_solver = predictions[algo_name][it]
                plot_data[logic][algo_name].append(self.db.get_score(solver=predicted_solver, benchmark=benchmark))

        for logic in plot_data:
            os.makedirs(f"{args.results}/{logic}", exist_ok=True)
            self.mk_par2_file(plot_data=plot_data[logic], path=f"{args.results}/{logic}/par2.csv")
            self.mk_plots(plot_data=plot_data[logic], path=f"{args.results}/{logic}/")



    def predict(self, benchmarks=None, include_predictions=False, selector = None):
        if benchmarks is None:
            benchmarks = self.db.get_benchmarks()
        if isinstance(benchmarks, Benchmark): benchmarks = [benchmarks]
        if selector is None: selector = self.default_selector
        return self.selectors[selector].predict(benchmarks=benchmarks, include_predictions=include_predictions)

    @staticmethod
    def load(path, with_db = True):
        ret = MachSMT(DataBase(build_on_init=False),train_on_init=False)
        with open(path, 'rb') as f:
            ret.selectors = pickle.load(f)
            if with_db:
                ret.db = pickle.load(f)
        return ret

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.selectors, f)
            pickle.dump(self.db, f)

    def mk_par2_file(self,plot_data,path):
        data = dict(
            (solver, sum(plot_data[solver]))
            for solver in plot_data
        )
        cols = ['Solver', 'Par-2 Score', 'Improvement']
        if 'MachSMT--EHM' in data:
            mach_score = data['MachSMT--EHM']
        elif 'machsmt-alloc' in data:
            mach_score = data['machsmt-alloc']
        else:
            mach_score = 0.0 

        with open(path, 'w') as outcsv:
            out = csv.DictWriter(outcsv, fieldnames=cols)
            out.writeheader()
            for solver in sorted(data, key=data.get):
                score = data[solver]
                mach_improve = (score - mach_score) / ((score + mach_score) / 2.0) 
                if isinstance(solver, Solver): solver = solver.get_name()
                out.writerow({cols[0]: solver, cols[1]: score, cols[2]: mach_improve})
                
    def mk_plots(self,plot_data, path, title=None,):

        max_score = 1200

        # Escape _ for latex
        if title:
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
        os.makedirs(path, exist_ok=True)

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
            if title:
                plt.title(title)
            plt.savefig(path+'{}.png'.format(plot_type), dpi=1000, bbox_inches='tight')
