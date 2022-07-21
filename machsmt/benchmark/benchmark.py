import os,pdb,sys,time,traceback
from collections import Iterable
from machsmt.parser import args as settings
from machsmt.util import die, warning
from machsmt.tokenize_sexpr import SExprTokenizer
from ..smtlib import grammatical_construct_list,logic_list,get_smtlib_file
from ..features import bonus_features
from func_timeout import func_timeout, FunctionTimedOut

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

    def get_logic(self):
        if not self.parsed: self.parse()
        return self.logic

    def get_track(self):
        if not self.parsed: self.parse()
        return self.track


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

    def compute_core_features(self):
        self.features = [0] * (len(grammatical_construct_list) + 2)
        self.features[-1] = float(os.path.getsize(self.path))   #benchmark file size

        def count_occurrences(sexprs, features):
            visit = sexprs[:]
            while visit:
                cur = visit.pop()
                if isinstance(cur, tuple):
                    visit.extend(cur)
                elif isinstance(cur, str):
                    if cur in keyword_to_index:
                        features[keyword_to_index[cur]] += 1
                else:
                    die("parsing error on: {} {}".format(self.path,
                                                         str(type(cur))))

        try:
            func_timeout(timeout=settings.feature_timeout,
                         func=count_occurrences,
                         args=(self.tokens, self.features))
        except FunctionTimedOut:
            warning('Timeout after {} seconds of compute_core_features on {}'.format(
                        settings.feature_timeout, self.name))
            self.features[-2] = 1


    def compute_bonus_features(self):
        timeout = settings.feature_timeout / len(bonus_features)
        for feat in bonus_features:
            try:
                ret = func_timeout(timeout=timeout,
                                   func=feat,
                                   args=(self.tokens[:],))
                if isinstance(ret, Iterable):
                    for r in ret:
                        self.features.append(float(r))
                else:
                    self.features.append(float(ret))
            except FunctionTimedOut:
                ret = feat([])
                if isinstance(ret, Iterable):
                    for r in ret:
                        self.features.append(-1.0)
                else:
                    self.features.append(-1.0)
                warning('Timeout after {} seconds of {} on {}'.format(
                            timeout, feat.__name__, self.name))
            except Exception as e:
                traceback.print_exc()
                die('Error in feature calculation on {}.'.format(self.name))

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
        try:
            assert self.logic in logic_list or self.logic == 'ALL'
        except AssertionError:
            warning(f"Logic: {self.logic} not expected.")
        try:
            assert self.check_sats >= 1
        except:
            die(f"No Check-Sat in {self}")
        self.track = 'SQ' if self.check_sats == 1 else 'INC'
        self.parsed = True

    def __str__(self): return self.name
    __repr__ = __str__

    def __hash__(self):
        return hash(str(self))
