import pdb,os,glob,sys,copy
from progress.bar import Bar
from smtzilla.search import get_inst_path
from smtzilla.compute_features import get_check_sat

WALL_TIMEOUT = 2400
TIMEOUT = 2398

class DB:
    def __init__(self):
        self.db = {}
        self.paths = {}

    def compute_score(self,theory,track,solver,inst):
        is_incr = track.lower().find('incremental') != -1 and track.lower().find('non-incremental') == -1

        if self.db[theory][track][solver][inst]['result'].find('unknown') != -1:
            return 2.0 * WALL_TIMEOUT
        if not is_incr and self.db[theory][track][solver][inst]['result'] != self.db[theory][track][solver][inst]['expected']:
            if self.db[theory][track][solver][inst]['expected'].lower().find('unknown') != -1:
                return float(self.db[theory][track][solver][inst]['wallclock time'])
            elif  self.db[theory][track][solver][inst]['result'].lower().find('unknown') >= 0:
                return 2.0 * WALL_TIMEOUT
            else:
                print("WRONG ANSWER!", solver, inst, theory, track, self.db[theory][track][solver][inst]['result'] ,self.db[theory][track][solver][inst]['expected'])
                return 10.0 * WALL_TIMEOUT
        elif is_incr:
            if int(self.db[theory][track][solver][inst]['wrong-answers']) != 0:
                print("WRONG ANSWER!", solver, inst, theory, track)
                return 10.0 * WALL_TIMEOUT
            if get_check_sat(get_inst_path(theory,inst)) == int(self.db[theory][track][solver][inst]['correct-answers']):
                if float(self.db[theory][track][solver][inst]['wallclock time']) < TIMEOUT:
                    return float(self.db[theory][track][solver][inst]['wallclock time'])
                else:
                    return 2.0 * WALL_TIMEOUT
            else:
                return 2.0 * WALL_TIMEOUT
        else:
            if float(self.db[theory][track][solver][inst]['wallclock time']) < TIMEOUT:
                return float(self.db[theory][track][solver][inst]['wallclock time'])
            else:
                return 2.0 * WALL_TIMEOUT
            return float(self.db[theory][track][solver][inst]['wallclock time'])

    def add(self,theory,track,solver,instance,data):
        if theory not in self.db:
            self.db[theory] = {}
        if track not in self.db[theory]:
            self.db[theory][track] = {}
        if solver not in self.db[theory][track]:
            self.db[theory][track][solver] = {}
        if instance not in self.db[theory][track][solver]:
            self.db[theory][track][solver][instance] = None
        self.db[theory][track][solver][instance] = data

    def build(self,year=2019):
        dir = 'smt-comp/' + str(year) + '/results/'
        data_files = glob.glob(dir + '*.csv')
        print("Building DB based on the following files: " + str(data_files))
        header = []
        benchmark_indx = None
        solver_index   = None
        for f in data_files:
            with open(f,'r') as file:
                it = 0
                for line in file.readlines():
                    if it == 0:
                        header = line.split(',')
                        header[-1] = header[-1][:-1]
                        print(header)
                        benchmark_indx = header.index('benchmark')
                        solver_indx    = header.index('solver')
                        it+=1
                        continue
                    line = line.split(',')
                    line[-1] = line[-1][:-1]
                    theory_benchmark = line[benchmark_indx].split('/')
                    theory = theory_benchmark[1]
                    solver = line[solver_indx]
                    benchmark = ''
                    for i in range(2,len(theory_benchmark)):
                        benchmark += theory_benchmark[i]
                    val = dict((header[i],line[i]) for i in range(len(header)))
                    self.add(theory,f.split('.')[0],solver,benchmark,val)
                    it+=1

    def tidy(self):
        self.clean_solvers()
        #self.clean_benchmarks()
        self.checker()

    def solver_merger(self,theory,track,solver_0,solver_1,new_name):
        self.db[theory][track][new_name] = {}
        for instance in self.db[theory][track][solver_0]:
            self.add(theory,track,new_name,instance,self.db[theory][track][solver_0][instance])
        for instance in self.db[theory][track][solver_1]:
            self.add(theory,track,new_name,instance,self.db[theory][track][solver_1][instance])
        self.db[theory][track].pop(solver_0)
        self.db[theory][track].pop(solver_1)

    
    def checker(self):
        pass

    def clean_solvers(self):
        for theory in self.db:
            for track in self.db[theory]:
                solver_counts = dict( (solver , len(self.db[theory][track][solver]))  for solver in self.db[theory][track])
                if min(list(solver_counts.values())) != max(list(solver_counts.values())):
                    print('Inconsistent solving counts for: ' + theory + ' ' + track, solver_counts,flush=True)
                    z3_solvers_wrapped = [solver for solver in solver_counts if solver.lower().find('z3') != -1 and solver.lower().find('wrap') != -1]
                    if len(z3_solvers_wrapped) == 2:
                        self.solver_merger(theory,track,z3_solvers_wrapped[0],z3_solvers_wrapped[1],'z3')
                        solver_counts = dict( (solver , len(self.db[theory][track][solver]))  for solver in self.db[theory][track])
                        if min(list(solver_counts.values())) == max(list(solver_counts.values())):
                            print("auto-fixed.")
                            continue
                        
                    print("FAILED TO AUTO FIX.")
                    sys.exit(1)

        print("Finished Cleaning Solvers!")

    def clean_benchmarks(self):
        inputs = set()
        
        print("Enumerating Inputs.", flush=True)
        for theory in self.db:
             for track in self.db[theory]:
                 first_solver = list(self.db[theory][track].keys())[0]
                 for solver in self.db[theory][track]:
                     assert len(self.db[theory][track][solver]) == len(self.db[theory][track][first_solver])
                     for instance in self.db[theory][track][first_solver]:
                         inputs.add((theory,instance))
        bar = Bar('Checking Existence of Inputs', max=len(inputs))
        remove = set()
        for theory,instance in inputs:
            v = get_inst_path(theory,instance)
            if v == None:
                remove.add(instance)
            bar.next()
        bar.finish()
        print("Total to be removed: " + str(len(remove)),flush=True)
        tmp_db = copy.deepcopy(self.db)
        for theory in self.db:
             for track in self.db[theory]:
                 for solver in self.db[theory][track]:
                     for instance in remove:
                         if instance in self.db[theory][track][solver]:
                             tmp_db[theory][track][solver].pop(instance)
        self.db = tmp_db

    def get_inst_path(self,theory,instance):
        path = 'benchmarks/' + theory + '/'
        instance_name = instance
        if os.path.exists(path + '/' + instance):
            return path + '/' + instance
        else:
            canidates = [None]
            while len(canidates) > 0:
                canidates = []
                directories = [v.split('/')[-2] for v in glob.glob(path+'*/')] 
                for dir in directories:
                    if instance_name.startswith(dir):
                        canidates.append(dir)
                best , longest = None,0
                for c in canidates:
                    if len(c) > longest:
                        best = c
                        longest = len(c)
                if best != None:         
                    path = path + best + '/'
                    instance_name = instance_name[len(best):]
        if os.path.exists(path + '/' + instance_name):
            return path + '/' + instance_name
        else:
            print("Failed to find: " + theory + ',' + instance)
            return None


    def summary(self):
        for theory in self.db:
            print(theory)
            for track in self.db[theory]:
                print("\t" + track)
                for solver in self.db[theory][track]:
                    print("\t\t" + solver + "\t" + str(len(self.db[theory][track][solver]))) 