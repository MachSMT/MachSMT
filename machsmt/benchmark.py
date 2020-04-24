import os,pdb,sys,time
import machsmt.settings as settings
from machsmt.util import die,get_smtlib_file
from machsmt.tokenize_sexpr import SExprTokenizer
from machsmt.smtlib import grammatical_construct_list

keyword_to_index = dict( (grammatical_construct_list[i],i) for i in range(len(grammatical_construct_list)))

class Benchmark:
    def __init__(self,path:str):
        try:
            self.path = path if os.path.exists(path) else get_smtlib_file(path)
        except FileNotFoundError:
            get_smtlib_file(path)
            die("Could not find: " + path)
        self.features = None
        self.theory = None
        self.timeout = False

    def compute_features(self):
        start = time.time()
        self.features = [0.0] * len(grammatical_construct_list)

        #recursion handle
        def get_constructs(sexpr):
            ret = {}
            for v in sexpr:
                if time.time() - start > settings.FEATURE_CALC_TIMEOUT:
                    self.timeout = True
                    return
                if isinstance(v,str) and v in keyword_to_index: self.features[keyword_to_index[v]] += 1.0
                elif isinstance(v,list): get_constructs(v)
                else: die("parsing error on: " + self.path + " " + str(type(v)))

            tokenizer = SExprTokenizer(self.path)
            for sexpr in tokenizer:
                if self.timeout: break
                get_constructs(sexpr)


    def get_features(self):
        if self.features != None: return self.features
        self.compute_features()
        return self.features
