import pdb,os,glob,sys,copy,pickle
from progress.bar import Bar
import machsmt.settings as settings
from machsmt.benchmark import Benchmark
from machsmt.solver import Solver 
from machsmt.util import die
import multiprocessing.dummy as mp ##?? other doesn't work for whatever reason...

class DB:
    def __init__(self):
        ## Core Storage
        self.benchmarks = {}
        self.solvers = {}


    def get_solvers(self):
        for solver in self.solvers: yield solver

    def get_benchmarks(self):
        for benchmark in self.benchmarks: yield str(benchmark)

    
    ##TODO FIX STORAGE TO USE SETS INSTEAD OF STR
    def __getitem__(self,key):
        if isinstance(key,str):
            if key in self.benchmarks and key in self.solvers: die("Database Error: Solver benchmark overlap.")
            elif key in self.benchmarks: return self.benchmarks[key]
            elif key in self.solvers: return self.solvers[key]
            else: raise IndexError
        if   len(key) == 0: raise IndexError
        elif len(key) == 1: return self[key[0]]
        elif len(key) == 2:
            s,b = None,None
            if key[0] in self.solvers: s = key[0]
            if key[1] in self.solvers: s = key[1]
            if key[0] in self.benchmarks: b = key[0]
            if key[1] in self.benchmarks: b = key[1]
            if s == None or b == None: raise IndexError
            return self.solvers[s].benchmarks[b]
    def load(self):
        print("Trying to load existing database.")
        if not os.path.exists(settings.LIB_DIR + '/db.dat'): raise FileNotFoundError
        with open(settings.LIB_DIR + '/db.dat', 'rb') as infile:
            self.benchmarks, self.solvers = pickle.load(infile)
            print("Succesfully loaded database.")
            return

    def save(self):
        if settings.SAVE_DB:
            if not os.path.exists(settings.LIB_DIR): os.mkdir(settings.LIB_DIR)
            with open(settings.LIB_DIR + '/db.dat', 'wb') as outfile:
                pickle.dump((self.benchmarks,self.solvers), outfile)
        

    def build(self,files):
        if isinstance(files,str): files = [files]
        
        n_lines,it_lines = 0,0
        for csvfile in files: 
            if not os.path.exists(csvfile): die("Could not find: " + csvfile)
            n_lines += sum(1 for line in open(csvfile))

        bar = Bar('Indexing Input Files', max=n_lines)
        for csvfile in files:
            benchmark_indx, solver_indx, score_indx = None,None,None
            with open(csvfile,'r') as file:
                it_file = 0
                for line in file:
                    line,it_file,it_lines  = line.split(','),it_file+1,it_lines+1
                    if it_file == 1: benchmark_indx, solver_indx, score_indx = line.index('benchmark'), line.index('solver'), line.index('wallclock time')
                    else:
                        benchmark,solver,score = line[benchmark_indx], line[solver_indx], float(line[score_indx])
                        if benchmark not in self.benchmarks: self.benchmarks[benchmark] = Benchmark(benchmark)
                        if solver not in self.solvers: self.solvers[solver] = Solver(solver)
                        self.solvers[solver].add_benchmark(self.benchmarks[benchmark],score)
                    bar.next()
        bar.finish()

        bar = Bar('Parsing Benchmark Files', max=len(self.benchmarks))
        mutex = mp.Lock()
        it = 0
        def mp_call(it_benchmark):
            it,benchmark = it_benchmark
            try:
                self.benchmarks[benchmark].parse()
                self.benchmarks[benchmark].compute_features()
            except: ##Fix for crash on large inputs, TODO: FIX SO CRASH DOESN"T HAPPEN
                print("Error parsing: " + str(benchmark), file=sys.stderr)
                if benchmark in self.benchmarks: self.benchmarks.pop(benchmark)
                for solver in self.solvers: self.solvers[solver].remove_benchmark(benchmark)

            mutex.acquire()
            bar.next()
            it += 1
            if it % 1000 == 0: self.save()
            mutex.release()

        with mp.Pool(settings.CORES) as pool:
            pool.map(mp_call,enumerate(self.benchmarks.keys()))
        self.save()
