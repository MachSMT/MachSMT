logic_list = [
    'ABVFP',
    'ALIA',
    'ANIA',
    'AUFBVDTLIA',
    'AUFDTLIA',
    'AUFLIA',
    'AUFLIRA',
    'AUFNIA',
    'AUFNIRA',
    'BV',
    'BVFP',
    'FP',
    'LIA',
    'LRA',
    'NIA',
    'NRA',
    'QF_ABV',
    'QF_ABVFP',
    'QF_ALIA',
    'QF_ANIA',
    'QF_AUFBV',
    'QF_AUFLIA',
    'QF_AUFNIA',
    'QF_AX',
    'QF_BV',
    'QF_AUFBVNIA',
    'QF_BVFP',
    'QF_BVFPLRA',
    'QF_DT',
    'QF_FP',
    'QF_FPLRA',
    'QF_IDL',
    'QF_LIA',
    'QF_LIRA',
    'QF_LRA',
    'QF_NIA',
    'QF_NIRA',
    'QF_NRA',
    'QF_RDL',
    'QF_S',
    'QF_SLIA',
    'QF_UF',
    'QF_UFBV',
    'QF_UFIDL',
    'QF_UFLIA',
    'QF_UFLRA',
    'QF_UFNIA',
    'QF_UFNRA',
    'UF',
    'UFBV',
    'UFDT',
    'UFDTLIA',
    'UFDTNIA',
    'UFIDL',
    'UFLIA',
    'UFLRA',
    'UFNIA',
]

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
    'Real',
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

]
