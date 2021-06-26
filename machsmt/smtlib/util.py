import os,glob,pdb
# from ..db import database as db 
OLD_DB = False


logic_list = ['ABV', 'ABVFP', 'ABVFPLRA', 'ALIA', 'ANIA', 'AUFBVDTLIA', 'AUFBVDTNIA', 'AUFDTLIA', 'AUFDTLIRA', 'AUFDTNIRA', 'AUFFPDTLIRA', 'AUFFPDTNIRA', 'AUFLIA', 'AUFLIRA', 'AUFNIA', 'AUFNIRA', 'AUFBV' 'BV', 'BVFP', 'BVFPLRA', 'FP', 'FPLRA', 'LIA', 'LRA', 'NIA', 'NRA', 'QF_ABV', 'QF_ABVFP', 'QF_ABVFPLRA', 'QF_ALIA', 'QF_ANIA', 'QF_AUFBV', 'QF_AUFBVLIA', 'QF_AUFBVNIA', 'QF_AUFLIA', 'QF_AUFNIA', 'QF_AX', 'QF_BV', 'QF_BVFP', 'QF_BVFPLRA', 'QF_DT', 'QF_FP', 'QF_FPLRA', 'QF_IDL', 'QF_LIA', 'QF_LIRA', 'QF_LRA', 'QF_NIA', 'QF_NIRA', 'QF_NRA', 'QF_RDL', 'QF_S', 'QF_SLIA', 'QF_UF', 'QF_UFBV', 'QF_UFBVLIA', 'QF_UFFP', 'QF_UFIDL', 'QF_UFLIA', 'QF_UFLRA', 'QF_UFNIA', 'QF_UFNRA', 'UF', 'UFBV', 'UFDT', 'UFDTLIA', 'UFDTLIRA', 'UFDTNIA', 'UFDTNIRA', 'UFFPDTLIRA', 'UFFPDTNIRA', 'UFIDL', 'UFLIA', 'UFLRA', 'UFNIA', 'UFNRA']


def get_theories(logic):
    _logic = logic[:].replace('QF_','').replace('IA','I').replace('RA','R')
    ret = []
    if _logic.find('A') != -1:
        ret.append('A')
    if _logic.find('BV') != -1:
         ret.append('BV')
    if _logic.find('R') != -1:
         ret.append('R')
    if _logic.find('I') != -1:
         ret.append('I')
    if _logic.find('FP') != -1:
         ret.append('FP')
    if _logic.find('S') != -1:
        ret.append('S')
    if _logic.find('UF') != -1:
        ret.append('UF')
    if _logic.find('DL') != -1:
        ret.append('DL')

    return ret

grammatical_construct_list = [
    'as',
    'assert',
    'check-sat',
    'check-sat-assuming',
    'declare-const',
    'declare-datatype',
    'declare-datatypes',
    'declare-fun',
    'declare-sort',
    'define-fun',
    'define-fun-rec',
    'define-funs-rec',
    'define-sort',
    'echo',
    'exit',
    'get-assertions',
    'get-assignment',
    'get-assignment',
    'get-info',
    'get-info',
    'get-model',
    'get-option',
    'get-option',
    'get-proof',
    'get-unsat-assumptions',
    'get-unsat-core',
    'get-value',
    'pop',
    'push',
    'reset',
    'reset-assertions',
    'set-info',
    'set-logic',
    'set-option',

    ##BINDERS
    'exists',
    'forall',
    'let',

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
    'extract',
    'bvnot',
    'bvand',
    'bvor',
    'bvneg',
    'bvadd',
    'bvmul',
    'bvudiv',
    'bvurem',
    'bvshl',
    'bvlshr',
    'bvult',
    'bvnand',
    'bvnor',
    'bvxor',
    'bvxnor',
    'bvcomp',
    'bvsub',
    'bvsdiv',
    'bvsrem',
    'bvsmod',
    'bvashr',
    'repeat',
    'zero_extend',
    'sign_extend',
    'rotate_left',
    'rotate_right',
    'bvule',
    'bvugt',
    'bvuge',
    'bvslt',
    'bvsle',
    'bvsgt',
    'bvsge',

    ##FP
    'RoundingMode',
    'FloatingPoint',
    'Float16',
    'Float32',
    'Float64',
    'Float128',
    'fp',

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
    'Real',


    'String',
    'RegLan',
    "str.++",
    "str.len",
    "str.<",
    "str.to_re",
    "str.in_re",
    "re.none",
    "re.all",
    "re.allchar",
    "re.++",
    "re.union",
    "re.inter",
    "re.*",
    "str.<=",
    "str.at",
    "str.substr",
    "str.prefixof",
    "str.suffixof",
    "str.contains",
    "str.indexof",
    "str.replace",
    "str.replace_all",
    "str.replace_re",
    "str.replace_re_all",
    "re.comp",
    "re.diff",
    "re.comp",
    "re.diff",
    "re.opt",
    "re.range",
    "re.range",
    "re.loop",
    "re.^",
    "str.is_digit",
    "str.to_code",
    "str.from_code",
    "str.to_int",
    "str.from_int",
]

def get_inst_path_core(logic,instance,path, instance_name):
    if os.path.exists(path + '/' + instance_name): return path + instance_name
    directories = [v.split('/')[-2] for v in glob.glob(path+'*/')]
    canidates = [dir for dir in directories if instance_name.startswith(dir)]
    canidates.sort(key=lambda x: len(x),reverse=True)
    for dir in canidates:
        ret = get_inst_path_core(logic,instance,path = path + dir + '/', instance_name = instance_name[len(dir):])
        if ret != None: return ret
    return None

cache = {}
def get_smtlib_file(name):
    global cache
    if os.path.exists(name): return name
    if name in cache: return cache[name] 
    split = name.split('/')
    for i in range(len(split)):
        if split[i] in logic_list:
            logic, inst = split[i], "".join([v for v in split[i+1:]])
            ret = get_inst_path_core(logic,inst,path='benchmarks/smt-lib/non-incremental' + '/' +  logic + '/', instance_name=inst)
            if ret == None:
                ret = get_inst_path_core(logic,inst,path='benchmarks/smt-lib/incremental' + '/' +  logic + '/', instance_name=inst)
            if ret == None: raise FileNotFoundError
            if OLD_DB:
                return ret.replace('smt-lib/incremental/','').replace('smt-lib/non-incremental/','')
            else:
                return ret
    raise FileNotFoundError

cache2 = {}
def get_checksats(path):
    global cache2

    old_path = path.replace('benchmarks/smt-lib/incremental/','benchmarks/').replace('benchmarks/smt-lib/non-incremental/', 'benchmarks/')
    try:
        assert db[old_path].check_sats > 0      ##Index Error if not in DB
        return db[old_path].check_sats
    except AssertionError:
        ret = 0
        with open(path,'r') as infile:
            for line in infile:
                if line.find('check-sat') != -1:
                    line = line[:line.find(';')]
                    ret += line.count('check-sat')
            return ret