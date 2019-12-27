import z3
import pdb
import sys, time,math,copy,random
import numpy as np
from sklearn.linear_model import Ridge
import itertools
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import AdaBoostRegressor
from sklearn import metrics
from sklearn.neural_network import MLPRegressor
TIMEOUT = 2400

keywords = [
    ##SMT-LIB
    'as',
    'let',
    'forall',
    'exists'
    '!',
    'set-logic',
    'set-option',
    'set-info',
    'declare-sort',
    'declare-fun',
    'declare-sort',
    'declare-fun',
    'define-fun',
    'push',
    'pop',
    'assert',
    'check-sat',
    'get-assertions',
    'get-proof',
    'get-unsat-core',
    'get-value',
    'get-assignment',
    'get-option',
    'get-info',
    'exit',


    ##CORE
    'true',
    'false',
    'not',
    '=>',
    'and',
    'or',
    'xor',
    '=',
    'distinct',
    'ite',
    'Bool',

    ##ARRAYS
    'Array',
    'select',
    'store',

    ##BV
    'BitVec',
    'concat',
    'bvnot',
    'bvneg',
    'bvand',
    'bvor',
    'bvadd',
    'bvmul',
    'bvudiv',
    'bvurem',
    'bvurem',
    'bvshl',
    'bvlshr',
    'bvult',

    ##FP
    'RoundingMode',
    'Real',
    'FloatingPoint',
    'Float16',
    'Float32',
    'Float64',
    'Float128',
    'fp'

    'roundNearestTiesToEven',
    'roundNearestTiesToAway',
    'roundTowardPositive',
    'roundTowardNegative',
    'roundTowardZero',

    'RNE',
    'RNA',
    'RTP',
    'RTN',
    'RTZ',

    'fp.abs',
    'fp.neg',
    'fp.add',
    'fp.sub',
    'fp.mul',
    'fp.div',
    'fp.fma',
    'fp.sqrt',
    'fp.rem',
    'fp.roundToIntegral',
    'fp.min',
    'fp.max',
    'fp.leq',
    'fp.lt',
    'fp.geq',
    'fp.gt',
    'fp.eq',
    'fp.isNormal',
    'fp.isSubnormal',
    'fp.isZero',
    'fp.isInfinite',
    'fp.isNaN',
    'fp.isNegative',
    'fp.isPositive',
    'to_fp',
    'to_fp_unsigned',
    'fp.to_ubv',
    'fp.to_sbv',
    'fp.to_real',


    ##INTS+REAL
    'Int',
    '-',
    '+',
    '*',
    'div',
    'mod',
    'abs',
    '<=',
    '<',
    '>=',
    '>',
    'to_real',
    'to_int',
    'is_int',

]


set_of_tokens = set(v for v in keywords)

#sys.setrecursionlimit(10**6)
# class Selector:
#     def __init__(self,db):
#         self.model = []
#         self.scaler = None
#         self.exp_split = 0.5
#         self.db = db.db
#     def build(self,features,labels,solvers):
#         X = copy.deepcopy(features)
#         Y = copy.deepcopy(labels)
#         random.shuffle(X)
#         random.shuffle(Y)

#         N = len(X)
#         M = len(Y[0])
#         self.model = [Ridge(alpha=1.0) for i in range(M)]

#         train_X = X[:round(self.exp_split * N)]
#         test_X  = X[round(self.exp_split * N) + 1):]
#         train_Y = Y[:round(self.exp_split * N)]
#         test_Y  = Y[(round(self.exp_split * N) + 1):]

#         predictions = []
#         for i in range(M):
#             self.model[i].fit(train_X, [math.log(v[i] + 1.0) for v in train_Y])

#         for i in range(N):
#             p = []
#             for j in range(M):
#                 p.append(self.model[j].predict(test_X[i]))
#             predictions.append(p)

#         plot_data = []

timeout = 5.0
start_time = time.time()

def z3_print(form,depth=0):
    print(('\t' * depth) + form.decl().name())
    for i in range(len(form.children())):
        z3_print(form.arg(i),depth+1)


def get_list_of_terms(form,ret=[]):
    if len(form.children()) == 0:
            return ret
    val = form.decl()
    if val not in ret:
        ret
    for i in range(len(form.children())):
        get_list_of_terms(form.arg(i),ret)
    return ret

def counter(form,ret={}):
    assert isinstance(form,z3.z3.AstVector) 
    terms = []
    for f in form:
        get_list_of_terms(f,terms)
    for t in terms:
        if t not in ret:
            ret[t] = 0
        ret[t] += 1
    return ret

def counter2(form,ret={}):
    if time.time() > start_time + timeout:
        return ret
    if len(form.children()) == 0:
        return ret
    try:
        val = form.decl()
    except:
        return ret

    if str(val) not in ret:
        ret[str(val)] = 1
    else:
        ret[str(val)] += 1
    for i in range(len(form.children())):
        try:
            counter2(form.arg(i),ret)
        except:
            pass
        if time.time() > start_time + timeout:
            return ret
    return ret
def counter_caller(form,ret={}):
    assert isinstance(form, z3.z3.AstVector)
    for f in form:
        counter2(f,ret)
        if time.time() > start_time + timeout:
            return ret
    return ret

def counter3(fname):
    ret = {}
    with open(fname,'r') as file:
        for line in file.readlines():
            line = line.replace('(', ' ( ')
            line = line.replace(')', ' ) ')
            if line.find(';') != -1:
                line = line[:line.find(';')]
            line = line.split()
            for t in line:
                if t in set_of_tokens:
                    if t not in ret:
                        ret[t] = 1
                    else:
                        ret[t] += 1
    return ret


def mk_ml_model():
    return Ridge(alpha=1.0)

class Model_Maker:
    def __init__(self,db):
        self.DB = db
        self.db = db.db
        self.feature_terms = {}
        self.solvers = {}
        self.models = {}


    def mk_model(self,theory,track):
        if theory not in self.feature_terms:
            self.feature_terms[theory] = {}
        self.feature_terms[theory][track] = set()
        if theory not in self.solvers:
            self.solvers[theory] = {}
        if theory not in self.models:
            self.models[theory] = {}
        self.solvers[theory][track] = list(self.db[theory][track].keys())
        self.solvers[theory][track].sort()
        self.models[theory][track] = {}
        counts = {}
        solvers = list(self.db[theory][track].keys())
        solvers.sort()
        tmp = []
        for s in solvers:
            if s.lower().find('par') != -1 and s.lower().find('4'):
                print("Removing: " + s)
                continue
            tmp.append(s)
        solvers = tmp


        for instance in self.db[theory][track][solvers[0]]:
            counts[instance] = self.compute_features(self.DB.get_inst_path(theory,instance))
            for t in counts[instance]:
                self.feature_terms[theory][track].add(t)
        self.feature_terms[theory][track] = list(self.feature_terms[theory][track])
        self.feature_terms[theory][track].sort()
        
        features = []
        labels = []
        instances = list(self.db[theory][track][solvers[0]].keys())
        random.shuffle(instances)
        for instance in instances:
            feat = []
            for term in self.feature_terms[theory][track]:
                if term in counts[instance]:
                    feat.append(counts[instance][term])
                else:
                    feat.append(0.0)
            features.append(feat)
            label = []
            for solver in solvers:
                rt = float(self.db[theory][track][solver][instance]['cpu time'])
                label.append(rt)
            labels.append(label)
    
        """
        EXPERIMENT
        """
        X = copy.deepcopy(features)
        Y = copy.deepcopy(labels)

        split = 0.5

        N = len(X)
        M = len(Y[0])

        train_instances = instances[:round(split * N)]
        test_instances  = instances[(round(split * N) + 1):] 
        train_X = X[:round(split * N)]
        test_X  = X[(round(split * N) + 1):]
        train_Y = Y[:round(split * N)]
        test_Y  = Y[(round(split * N) + 1):]



        for s in solvers:
            self.models[theory][track][s] = make_pipeline(StandardScaler(), PCA(n_components=min(10, len(train_X[0]))),           
            #MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=10000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=10)
            AdaBoostRegressor()
            
            )

        predictions = []
        for i in range(M):
            self.models[theory][track][solvers[i]].fit(train_X, [math.log(v[i] + 1.0) for v in train_Y])

        for i in range(len(test_X)):
            p = []
            for solver in solvers:
                p.append(self.models[theory][track][solver].predict([test_X[i]]))
            predictions.append(p)

        plot_data = []
        for s in solvers:
            data = [s,[]]
            for instance in test_instances:
                data[1].append(float(self.db[theory][track][s][instance]['cpu time']))
            data[1].sort()
            plot_data.append(data)
        
        predicted_runtimes = []
        for i in range(len(predictions)):
            pred = predictions[i]
            instance = test_instances[i]
            predicted_runtimes.append(float(self.db[theory][track][solvers[np.argmin(pred)]][instance]['cpu time']))
        predicted_runtimes.sort()
        plot_data.append(['ml_model', predicted_runtimes])


        vb_runtimes = []
        for instance in test_instances:
            rts = []
            for s in solvers:
                rts.append(float(self.db[theory][track][s][instance]['cpu time']))
            vb_runtimes.append(np.min(rts))
        vb_runtimes.sort()
        plot_data.append(['virtual best', vb_runtimes])


        import pylab
        figData = pylab.figure()
        ax = pylab.gca()


        marker = itertools.cycle((',', '+', '.', 'o', '*'))
        for data in plot_data:
            pylab.plot([v for v in data[1] if v < TIMEOUT], label=data[0] ,marker=next(marker))
            assert len(data) == len(plot_data[0]), data
            par2 = 0.0
            for v in data[1]:
                if v < TIMEOUT:
                    par2 += v
                else:
                    par2 += TIMEOUT * 2.0
            print(data[0], par2)
        figLegend = pylab.figure(figsize = (1.5,1.3))
        pylab.figlegend(*ax.get_legend_handles_labels(), loc = 'upper left')

        x = random.randint(0,1000000)
        figData.savefig(theory + '_' + str(x) + ".png")
        figLegend.savefig(theory + '_' + str(x) + "legend.png")        

    def compute_features(self,file):
        # global start_time
        # z3input = z3.parse_smt2_file(file)
        # assert isinstance(z3input,z3.z3.AstVector)
        # ret = {}
        # start_time = time.time()
        # counter_caller(z3input,ret)
        # print(file, ret, time.time() - start_time,flush=True)
        start_time = time.time()
        ret = counter3(file)
        #print(file, ret, time.time() - start_time,flush=True)
        return ret
