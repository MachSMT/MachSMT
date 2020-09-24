import os,pdb,sys,time,traceback
from collections import Iterable
from machsmt.parser import args as settings
from machsmt.util import die, warning
from machsmt.tokenize_sexpr import SExprTokenizer
from ..smtlib import grammatical_construct_list,logic_list,get_smtlib_file
from ..features import bonus_features
from func_timeout import func_timeout, FunctionTimedOut
# import ..extra_features

keyword_to_index = dict( (grammatical_construct_list[i],i) for i in range(len(grammatical_construct_list)))

class Benchmark:
    def __init__(self,name:str):
        self.name       = name
        self.path       = name if os.path.exists(name) else get_smtlib_file(name)
        self.features   = None
        self.theory     = None
        self.timeout    = False
        self.logic      = 'ALL'
        self.track      = 'UNKNOWN' ## 'SQ' or 'INC'
        self.family     = None
        self.check_sats = 0
        self.score      = None
        self.graph      = None
        self.parsed     = False
        self.tokens     = []
        self.total_feature_time = float('nan')
        # pdb.set_trace()

    def make_graph(self):
        pass

    def traverse_tokens(self,yield_tuples=True): ## bit buggy checking in for now.
        if not self.tokens: self.tokens = [sexpr for sexpr in SExprTokenizer(self.path)]
        cache = set()
        visit = self.tokens[:]
        # visit.reverse()
        while visit:
            token = visit.pop()
            if token in cache: continue
            if isinstance(token, tuple):
                visit.extend(token)
                cache.add(token)
                if yield_tuples: continue
            yield token
        self.tokens = []

    ## Compute Features up to a timeout
    def compute_features(self): 
        if not self.tokens: self.tokens = [sexpr for sexpr in SExprTokenizer(self.path)]
        start = time.time()

        self.compute_core_features()
        if settings.semantic_features: self.compute_bonus_features()

        self.total_feature_time = time.time() - start
        self.tokens = []

    def compute_core_features(self): ##TODO: replace with a proper traversal, get rid of recursion catch!!!!
        start = time.time()
        self.features = [0] * (len(grammatical_construct_list) + 2)
        #recursion handle
        def get_constructs(sexpr):
            ret = {}
            for v in sexpr:
                if time.time() - start > settings.feature_timeout:
                    self.timeout = True
                    return
                if isinstance(v,str): 
                    if v in keyword_to_index: self.features[keyword_to_index[v]] += 1
                elif isinstance(v,tuple): get_constructs(v)
                else: die("parsing error on: " + self.path + " " + str(type(v)))

        self.features[-2] = 1 if self.timeout else -1           #feature calc timeout?
        self.features[-1] = float(os.path.getsize(self.path))   #benchmark file size

        for sexpr in self.tokens:
            if self.timeout: break
            try:                    get_constructs(sexpr)
            except RecursionError:  pass


    def compute_bonus_features(self):
        for feat in bonus_features:
            timeout = settings.feature_timeout / len(bonus_features)
            try:
                ret = func_timeout(
                    timeout=settings.feature_timeout / len(bonus_features), 
                    func=feat, 
                    kwargs={'tokens':self.tokens[:]},
                )
                if isinstance(ret, Iterable):
                    for r in ret:
                        self.features.append(float(r))
                else:
                    self.features.append(float(ret))
                fail = False
            except RecursionError:
                fail = True
                warning(f"Recursion limit hit on {self.name} with feature {feat}. Treating as timeout.")
            except FunctionTimedOut:
                fail = True
                warning('Timeout after {} seconds of {} on {}'.format(
                            timeout, feat.__name__, self.name))
            except Exception as e:
                traceback.print_exc()
                die('Error in feature calculation.')
            if fail:
                ret = feat([])
                if isinstance(ret, Iterable):
                    for r in ret:
                        self.features.append(-1.0)
                else:
                    self.features.append(-1.0)


    ## Get and if necessary, compute features.
    def get_features(self):
        if self.features != None: return self.features
        self.compute_features()
        return self.features

    # full parsing of input file.
    # compute logic, track, # check-sat
    def parse(self):
        if self.parsed: return
        self.tokens = [sexpr for sexpr in SExprTokenizer(self.path)]
        for sexpr in self.tokens:
            if len(sexpr) >  0 and sexpr[0] == 'check-sat': self.check_sats += 1
            if len(sexpr) >= 2 and sexpr[0] == 'set-logic': self.logic = sexpr[1]
        assert self.logic in logic_list or self.logic == 'ALL'
        assert self.check_sats >= 1
        self.track = 'SQ' if self.check_sats == 1 else 'INC'
        self.parsed = True

    def __str__(self): return self.name
    __repr__ = __str__

    def __hash__(self):
        return hash(str(self))
