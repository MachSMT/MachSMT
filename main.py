import glob , pdb
from db import DB
year = 2019
dir = 'smt-comp/' + str(year) + '/results/' 
data_files = glob.glob(dir + '*.csv')

db = DB()

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
            db.add(theory,solver,benchmark,val)
            it+=1
db.summary()
