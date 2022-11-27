import os
import pickle
import csv
from alive_progress import alive_bar
from ..config import args
from ..benchmark import Benchmark
from ..solver import Solver
from ..util import warning, die
from ..exceptions import MachSMT_BadCSVError
from multiprocessing.pool import ThreadPool as Pool

def process_benchmark(benchmark):
    benchmark.parse()
    return benchmark

class DataBase:
    def __init__(self, files=[], build_on_init=True):
        self.benchmarks = {}
        self.solvers = {}
        if build_on_init: self.build(files)

    def check_files(self, files):
        for file in files:
            assert os.path.exists(file)

    def get_solver(self, solver_name): return self.solvers[solver_name]

    def get_solvers(self, benchmark=None, logic=None):
        ret = []
        for solver in self.solvers:
            if benchmark is not None and benchmark not in self.solvers[solver].benchmarks:
                continue
            if logic is not None:
                ok = False
                for bench in self.get_benchmarks(solver=solver):
                    if self.benchmarks[bench].logic == logic:
                        ok = True
                        break
                if not ok:
                    continue
            ret.append(solver)
        return tuple(self.solvers[s] for s in sorted(ret))

    def get_benchmarks(self, solver=None, logic=None):
        ret = []
        for benchmark in self.benchmarks:
            if solver is not None:
                if benchmark not in self.solvers[solver].benchmarks:
                    continue
            if logic is not None:
                if self.benchmarks[benchmark].logic != logic:
                    continue
            ret.append(benchmark)
        return tuple(self.benchmarks[b] for b in sorted(ret))

    def get_logics(self, solver=None):
        ret = set()
        for benchmark in self.get_benchmarks():
            if solver is not None:
                if benchmark not in self.solvers[solver].benchmarks:
                    continue
            ret.add(benchmark.logic)
        return tuple(sorted(ret))

    def get_score(self, solver, benchmark):
        if isinstance(solver, str):
            solver = self.solvers[solver]
        if isinstance(benchmark, str):
            benchmark = self.benchmarks[benchmark]
        return self.solvers[solver.get_name()].scores[benchmark.get_path()]

    def __len__(self): return len(self.benchmarks)

    def load(self, loc=args.lib, name='db.machsmt'):
        if not os.path.exists(loc):
            raise FileNotFoundError
        with open(f"{loc}/{name}", 'rb') as infile:
            self.benchmarks, self.solvers = pickle.load(infile)
            return

    def save(self, loc=args.lib, name='db.machsmt'):
        if not os.path.exists(loc):
            os.makedirs(loc)
        with open(f"{loc}/{name}", 'wb') as outfile:
            pickle.dump((self.benchmarks, self.solvers), outfile)

    def build(self, files=[]):
        if isinstance(files, str):
            files = [files]
        for file in files:
            self.parse_csv_file(file)
        with alive_bar(len(self.benchmarks), title='Processing Benchmark Files') as bar:
            with Pool(processes=args.cores) as pool:
                for _, parsed_benchmark in enumerate(
                    pool.imap_unordered(
                        process_benchmark, self.benchmarks.values(), 1)):
                    if parsed_benchmark:
                        self.benchmarks[parsed_benchmark.get_path()] = parsed_benchmark
                    else:
                        die(f"Error processing {parsed_benchmark}. Skipping for now...")
                    bar()

    def parse_csv_file(self, file):
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Could not find file: {file}, cwd={os.getcwd()}")
        required = ['benchmark', 'solver', 'score']
        with open(file) as csvfile:
            lines = sum(1 for line in csvfile) - 1
        with alive_bar(lines, title='Parsing Input File') as bar:
            with open(file) as csvfile:
                reader = csv.DictReader(csvfile)
                for req in required:
                    if req not in reader.fieldnames:
                        raise MachSMT_BadCSVError
                for it, row in enumerate(reader):
                    benchmark, solver, score = row['benchmark'], row['solver'], float(row['score'])
                    if not os.path.isfile(benchmark):
                        warning(f'Skipping {file}:{it+1}, no file {benchmark}')
                        continue
                    if benchmark not in self.benchmarks:
                        self.benchmarks[benchmark] = Benchmark(benchmark)
                    if solver not in self.solvers:
                        self.solvers[solver] = Solver(solver)
                    self.solvers[solver].add_benchmark(self.benchmarks[benchmark], score)
                    self.benchmarks[benchmark].add_solver(self.solvers[solver], score)
                    bar()

    def is_complete(self):
        for it, benchmark in enumerate(self.get_benchmarks()):
            if it == 0:
                N = len(benchmark.get_solvers())
            else:
                if N != len(benchmark.get_solvers()):
                    return False
        for it, solver in enumerate(self.get_solvers()):
            if it == 0:
                N = len(solver.get_benchmarks())
            else:
                if N != len(solver.get_benchmarks()):
                    return False

        return True

    def __str__(self):
        return f"DataBase(len(self.benchmarks)={len(self.benchmarks)} len(self.solvers)={len(self.solvers)})"
