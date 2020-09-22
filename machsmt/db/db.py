import pdb,os,glob,sys,copy,pickle, traceback
from progress.bar import Bar
from ..parser import args as settings
from ..benchmark import Benchmark
from ..solver import Solver
from ..util import die,warning
import multiprocessing.dummy as mp ##?? other doesn't work for whatever reason...

class DB:
    def __init__(self):
        ## Core Storage
        self.benchmarks = {}
        self.solvers = {}

    def get_solvers(self,benchmark=None,logic=None,track=None): 
        for solver in self.solvers:
            if benchmark != None and benchmark not in self.solvers[solver].benchmarks: continue
            if logic != None:
                ok = False
                for bench in self.get_benchmarks(solver=solver):
                    if self.benchmarks[bench].logic == logic:
                        ok = True
                        break
                if not ok: continue
            if track != None:
                ok = False
                for bench in self.solvers[solver].benchmarks:
                    if self.benchmarks[bench].track == track:
                        ok = True
                        break
                if not ok: continue
            yield solver

    def get_tracks(self,solver=None,logic=None):
        ret = set()
        for benchmark in self.get_benchmarks():
            if solver != None and logic != None:
                if self.benchmarks[benchmark].logic == logic and benchmark in self.solvers[solver].benchmarks:
                    ret.add(self.benchmarks[benchmark].track)
            elif logic != None: 
                if self.benchmarks[benchmark].logic == logic: ret.add(self.benchmarks[benchmark].track)
            elif solver != None:
                if benchmark in self.solvers[solver].benchmarks:
                    ret.add(self.benchmarks[benchmark].track)
            else: ret.add(self.benchmarks[benchmark].track)
        return ret

    def get_benchmarks(self,solver=None,logic=None,track=None): 
        for benchmark in self.benchmarks:
            if solver != None:
                if benchmark not in self.solvers[solver].benchmarks: continue
            if logic != None:
                if self.benchmarks[benchmark].logic != logic: continue
            if track != None:
                if self.benchmarks[benchmark].track != track: continue

            yield benchmark

    def get_logics(self,solver=None,track=None):
        ret = set()
        for benchmark in self.get_benchmarks():
            if solver != None:
                if benchmark not in self.solvers[solver].benchmarks: continue
            if track != None:
                if self.benchmarks[benchmark].track != track: continue
            ret.add(self.benchmarks[benchmark].logic)
        return ret

    def __getitem__(self,key):
        if isinstance(key,str):
            if key in self.benchmarks and key in self.solvers: die("Database Error: Solver benchmark overlap.")
            elif key in self.benchmarks: return self.benchmarks[key]
            elif key in self.solvers: return self.solvers[key]
            else: raise IndexError("Could not find: " + str(key) + " in database.")
        if   len(key) == 0: raise IndexError("Could not find: " + str(key) + " in database.")
        elif len(key) == 1: return self[key[0]]
        elif len(key) == 2:
            s,b = None,None
            if key[0] in self.solvers: s = key[0]
            if key[1] in self.solvers: s = key[1]
            if s == None:
                raise IndexError("Could not find: " + str(key) + " in database.")
            if   key[0] in self.solvers[s].benchmarks:  b = key[0]
            elif key[1] in self.solvers[s].benchmarks:  b = key[1]
            else: 
                raise IndexError("Could not find: " + str(key) + " in database.")
            return self.solvers[s].benchmarks[b]

    def __len__(self): return len(self.benchmarks)

    def load(self):
        print("Trying to load existing database.")
        if not os.path.exists(settings.lib + '/db.dat'): raise FileNotFoundError
        with open(settings.lib + '/db.dat', 'rb') as infile:
            self.benchmarks, self.solvers = pickle.load(infile)
            print("Succesfully loaded database.")
            return

    def save(self):
        if not os.path.exists(settings.lib): os.mkdir(settings.lib)
        with open(settings.lib + '/db.dat', 'wb') as outfile:
            pickle.dump((self.benchmarks,self.solvers), outfile)
        
    def build(self,files):
        if isinstance(files,str): files = [files]
        
        n_lines,it_lines = 0,0
        for csvfile in files: 
            if not os.path.exists(csvfile): die("Could not find: " + csvfile)
            n_lines += sum(1 for line in open(csvfile)) -1 

        bar = Bar('Indexing Input Files', max=n_lines)
        for csvfile in files:
            ## SQ Data
            benchmark,solver,wallclock_time,result,expected = None,None,None,None,None
            ##INC Data
            benchmark,solver,wallclock_time,result,wrong_answers,correct_answers = None,None,None,None,None,None
            ##Data Type
            is_sq, is_inc = False,False

            with open(csvfile,'r') as file:
                it_file = 0
                for line in file:
                    line,it_file,it_lines  = line.split(','),it_file+1,it_lines+1
                    if len(line) > 0 and len(line[-1]) > 0 and line[-1][-1] == '\n': line[-1] = line[-1][:-1]
                    if it_file == 1: benchmark_indx, solver_indx, score_indx = line.index('benchmark'), line.index('solver'), line.index('score')
                    else:
                        try:
                            benchmark,solver,score = line[benchmark_indx], line[solver_indx], float(line[score_indx])
                            if benchmark not in self.benchmarks: self.benchmarks[benchmark] = Benchmark(benchmark)
                            if solver not in self.solvers: self.solvers[solver] = Solver(solver)
                            self.solvers[solver].add_benchmark(benchmark,score)
                            bar.next()
                        except FileNotFoundError:
                            warning("Missing File: ", benchmark, "skipping for now...")
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
                traceback.print_exc()
                pdb.set_trace()
                warning("Error parsing: " + str(benchmark), file=sys.stderr)
                if benchmark in self.benchmarks: self.benchmarks.pop(benchmark)
                for solver in self.solvers: self.solvers[solver].remove_benchmark(benchmark)

            mutex.acquire()
            bar.next()
            it += 1
            if it % 1000 == 0: self.save()
            mutex.release()
        with mp.Pool(os.num_cores()) as pool:
            pool.map(mp_call,enumerate(self.benchmarks.keys()))
        bar.finish()
   