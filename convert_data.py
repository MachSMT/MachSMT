## script takes in files from the smt-comp github repo
## and converts it to a benchmark,solver,score
## csv file by printing it to stdout

import sys,argparse,pdb,sys,traceback
from machsmt.benchmark import Benchmark
import multiprocessing as mp

TIMEOUT = 2400
attributes = 'benchmark', 'solver', 'wallclock time', 'result', 'expected','correct-answers','wrong-answers'

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--data-files",
                metavar="files[,files...]",
                action="store",
                dest="files",
                default=None,
                nargs='+',
                help="Input Data files containing solver, benchmark, runtime pairs")
args = parser.parse_args()


data_points = [] ##storage

for file in args.files:
    with open(file,'r') as infile:
        it_line = 0
        index = {}
        for line in infile.readlines():
            line = line.split(',')
            if line[-1][-1] == '\n': line[-1] = line[-1][:-1] ##kill \n at end
            it_line += 1
            if it_line == 1:                ##get attr index in csv
                for token in attributes:
                    try: index[token] = line.index(token)
                    except ValueError: pass
            else:                           ##parse line
                data_point = {}
                for token in index: data_point[token] = line[index[token]]
                data_points.append(data_point)

# import random
# random.shuffle(data_points)
print("benchmark,solver,score",flush=True)  # output header
mutex = mp.Lock()

benchmarks = {}

def mp_call(point):
    try:
        b = None
        b = Benchmark(point['benchmark'])
        if b.path in benchmarks: b = benchmarks[b.path]
        else: b.parse()
        score = None
        if 'result' in point and point['result'] == '--': ##treat '--' as unknown
            point['result'] = 'starexec-unknown'
        if b.check_sats == 1:
            try:    ## compute score from SQ styled input file
                if point['result'] != point['expected'] and point['expected'] != 'starexec-unknown' and point['result'] != 'starexec-unknown':
                    score = 10 * TIMEOUT
                elif float(point['wallclock time']) >= TIMEOUT or point['result'] == 'starexec-unknown': score = 2 * TIMEOUT
                else: score = float(point['wallclock time'])
            except KeyError: ## compute score from INC styled input file
                if int(point['wrong-answers']) > 0: score = 10 * TIMEOUT
                elif int(point['correct-answers']) == 0: score = 2 * TIMEOUT
                else: score = float(point['wallclock time'])
        else: ##INC equation
            score = float(point['wallclock time']) + (2 * TIMEOUT / b.check_sats) * (b.check_sats - int(point['correct-answers'])) + 10 * TIMEOUT * int(point['wrong-answers'])
        mutex.acquire()
        print(b.path + ',' + point['solver'] + ',' + str(score),flush=True)
        if b.path not in benchmarks: benchmarks[b.path] = b
        mutex.release()
    except Exception as ex:
        traceback.print_exception(type(ex), ex, ex.__traceback__)
        print('error: ' + str(point),file=sys.stderr,flush=True)

with mp.Pool(mp.cpu_count()) as pool:
    pool.map(mp_call,data_points)
