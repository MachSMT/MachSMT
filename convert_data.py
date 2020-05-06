import sys,argparse,pdb,sys,traceback
from machsmt.benchmark import Benchmark
import multiprocessing.dummy as mp

print("benchmark,solver,score",flush=True)

is_sq, is_inc = False,False
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

data_points = []
args = parser.parse_args()
for file in args.files:
    with open(file,'r') as infile:
        it_line = 0
        index = {}
        for line in infile.readlines():
            line = line.split(',')
            if line[-1][-1] == '\n': line[-1] = line[-1][:-1]
            it_line += 1
            if it_line == 1:
                for token in attributes:
                    try: index[token] = line.index(token)
                    except ValueError: pass
            else:
                data_point = {}
                for token in index: data_point[token] = line[index[token]]
                data_points.append(data_point)

# import random
# random.shuffle(data_points)

mutex = mp.Lock()
def mp_call(point):
    try:
        b = Benchmark(point['benchmark'])
        b.parse()
        score = None
        if 'result' in point and point['result'] == '--': 
            point['result'] = 'starexec-unknown'
        if b.check_sats == 1:
            try:
                if point['result'] != point['expected'] and point['expected'] != 'starexec-unknown' and point['result'] != 'starexec-unknown':
                    score = 10 * TIMEOUT
                elif float(point['wallclock time']) >= TIMEOUT or point['result'] == 'starexec-unknown': score = 2 * TIMEOUT
                else: score = float(point['wallclock time'])
            except KeyError:
                if int(point['wrong-answers']) > 0: score = 10 * TIMEOUT
                elif int(point['correct-answers']) == 0: score = 2 * TIMEOUT
                else: score = float(point['wallclock time'])
        else:
            score = float(point['wallclock time']) + (2 * TIMEOUT / b.check_sats) * (b.check_sats - int(point['correct-answers'])) + 10 * TIMEOUT * int(point['wrong-answers'])
        mutex.acquire()
        print(b.path + ',' + point['solver'] + ',' + str(score),flush=True)
        mutex.release()
    except Exception as ex:
        traceback.print_exception(type(ex), ex, ex.__traceback__)
        print('error: ' + str(point),file=sys.stderr,flush=True)

with mp.Pool(mp.cpu_count()) as pool:
    pool.map(mp_call,data_points)
